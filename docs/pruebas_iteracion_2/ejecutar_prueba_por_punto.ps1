param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet(
        'P2-01',
        'P2-02',
        'P2-03',
        'P2-06-EVAL',
        'P2-06-DECISION',
        'P2-06-BLOQUEO',
        'P2-07',
        'P2-10',
        'P2-11',
        'P2-13-ENVIO-PERMANENTE',
        'P2-13-ENVIO-EVENTUAL',
        'P2-13-ACTIVO',
        'P2-15',
        'P2-16-17'
    )]
    [string]$Punto
)

$tests = @{
    'P2-01' = @{
        Description = 'Rechazo de registro cuando falta un campo obligatorio.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_registration_rejects_missing_fields_and_checks_priority_boundaries'
    }
    'P2-02' = @{
        Description = 'Guardado y consulta posterior de solicitudes permanentes y eventuales.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_permanent_and_eventual_registration_persist_and_reload'
    }
    'P2-03' = @{
        Description = 'Prioridad en los limites de 0, 3, 4, 7 y 8 dias.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_registration_rejects_missing_fields_and_checks_priority_boundaries'
    }
    'P2-06-EVAL' = @{
        Description = 'Conservacion de evaluaciones de Planta Tecnica y Sistemas.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_commercial_approval_preserves_evaluations_and_resolution_note'
    }
    'P2-06-DECISION' = @{
        Description = 'Registro de la decision final de aprobacion o rechazo comercial.'
        Test = @(
            'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_commercial_approval_preserves_evaluations_and_resolution_note',
            'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_commercial_rejection_is_persisted_and_blocks_execution'
        )
    }
    'P2-06-BLOQUEO' = @{
        Description = 'Una solicitud rechazada no avanza a la asignacion tecnica.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_commercial_rejection_is_persisted_and_blocks_execution'
    }
    'P2-07' = @{
        Description = 'Conservacion de la observacion original y la explicacion comercial.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_commercial_approval_preserves_evaluations_and_resolution_note'
    }
    'P2-10' = @{
        Description = 'Registro del cronograma tentativo asociado a solicitud y actividad.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_installation_schedule_submission_approval_and_reload'
    }
    'P2-11' = @{
        Description = 'Diferencia entre horario tentativo y aprobado; conservacion y recarga.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_installation_schedule_submission_approval_and_reload'
    }
    'P2-13-ENVIO-PERMANENTE' = @{
        Description = 'Enviar la conclusion permanente no la aprueba automaticamente.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_permanent_conclusion_requires_support_approval_for_active_link'
    }
    'P2-13-ENVIO-EVENTUAL' = @{
        Description = 'Enviar la conclusion eventual no la aprueba automaticamente.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_eventual_service_stays_open_until_removal_and_final_review'
    }
    'P2-13-ACTIVO' = @{
        Description = 'Aprobar conclusion permanente finaliza la solicitud y muestra el enlace activo.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_permanent_conclusion_requires_support_approval_for_active_link'
    }
    'P2-15' = @{
        Description = 'La solicitud eventual conserva su periodo y deja pendiente el retiro.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_eventual_service_stays_open_until_removal_and_final_review'
    }
    'P2-16-17' = @{
        Description = 'La aprobacion del retiro permite aprobar la conclusion eventual.'
        Test = 'DATALAN.test_iteration2_postgresql.Iteration2PostgreSQLTests.test_eventual_service_stays_open_until_removal_and_final_review'
    }
}

$repositoryRoot = (Get-Location).Path
$projectDirectory = Join-Path $repositoryRoot 'DATALAN'
if (-not (Test-Path (Join-Path $projectDirectory 'manage.py'))) {
    throw 'Ejecuta este comando desde la raiz del repositorio DATALAN.'
}

$python = Join-Path $repositoryRoot 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    throw "No se encontro el interprete esperado: $python"
}

$test = $tests[$Punto]
$capture = Join-Path $env:TEMP "datalan-$Punto-$PID.txt"
$testLabels = @($test.Test) -join ' '
$command = "..\venv\Scripts\python.exe manage.py test $testLabels --verbosity 2"

$env:DJANGO_SETTINGS_MODULE = 'DATALAN.settings_iteration2_test'
Write-Output "FECHA: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
Write-Output "PUNTO: $Punto"
Write-Output "COMPROBACION: $($test.Description)"
Write-Output 'TIPO: Prueba de integracion PostgreSQL con base exclusiva datalan_it2_test.'
Write-Output "COMANDO: $command"
Write-Output '----- SALIDA REAL DE DJANGO -----'

$process = $null
try {
    $cmdArguments = '/d /c ""' + $python + '" manage.py test ' + $testLabels +
        ' --verbosity 2 > "' + $capture + '" 2>&1"'
    $process = Start-Process `
        -FilePath $env:ComSpec `
        -ArgumentList $cmdArguments `
        -WorkingDirectory $projectDirectory `
        -NoNewWindow `
        -Wait `
        -PassThru

    Get-Content -LiteralPath $capture
    Write-Output "RETURN_CODE=$($process.ExitCode)"
}
finally {
    if (Test-Path -LiteralPath $capture) {
        Remove-Item -LiteralPath $capture
    }
}

if ($process.ExitCode -ne 0) {
    exit $process.ExitCode
}
