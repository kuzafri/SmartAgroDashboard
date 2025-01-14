<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Improve Existing Model</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0 auto;
            padding: 20px;
        }

        .cell {
            border: 1px solid #ccc;
            margin-bottom: 20px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 8px;
        }

        .output-area {
            background-color: #f0f0f0;
            padding: 10px;
            margin-top: 10px;
            white-space: pre-wrap;
            font-family: monospace;
            border-radius: 8px;
        }

        .trainbutton {
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h3 class="text-center">Improve Existing Model</h3>

        <div class="mb-4">
            <h4>Load Model</h4>
            <button onclick="listModels()" class="btn btn-secondary mt-2">Refresh Models</button>
            <!-- <button onclick="listModels()" class="btn btn-primary">List Models</button> -->
            <select id="modelSelect" class="form-control mt-2" style="display: none;"></select>
            <button onclick="loadModel()" class="btn btn-primary mt-2">Load Selected Model</button>
        </div>

        <h4>Improve Model</h4>
        <div id="notebook">
            <div class="cell">
                <form class="training-form">
                    <table class="table table-bordered">
                        <thead class="thead-light">
                            <tr>
                                <th>BANK</th>
                                <th>HVCORNER</th>
                                <th>IO</th>
                                <th>CAP</th>
                                <th>POWERH</th>
                                <th>POWER</th>
                                <th>GROUND</th>
                                <th>PROBE</th>
                                <th>FUSE</th>
                                <th>LABEL</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><input type="text" name="bank" class="form-control"></td>
                                <td><input type="number" name="hvcorner" class="form-control"></td>
                                <td><input type="number" name="io" class="form-control"></td>
                                <td><input type="number" name="cap" class="form-control"></td>
                                <td><input type="number" name="powerh" class="form-control"></td>
                                <td><input type="number" name="power" class="form-control"></td>
                                <td><input type="number" name="ground" class="form-control"></td>
                                <td><input type="number" name="probe" class="form-control"></td>
                                <td><input type="number" name="fuse" class="form-control"></td>
                                <td><input type="number" name="label" class="form-control"></td>
                            </tr>
                        </tbody>
                    </table>
                    <button class="btn btn-success trainbutton" type="submit">Train Model</button>
                </form>
                <div class="output-area mt-2"></div>
            </div>
        </div>

        <button onclick="addCell()" class="btn btn-secondary mt-4">Add Cell</button>

        <div class="mt-4">
            <h4>Save Improved Model</h4>
            <input type="text" id="modelName" class="form-control" placeholder="Enter model name">
            <button onclick="saveImprovedModel()" class="btn btn-primary mt-2">Save Improved Model</button>
        </div>
    </div>

    <script>

        $(document).ready(function() {
            listModels();
        });

        let modelLoaded = false;

        function deleteModel(modelName) {
            if (confirm("Are you sure you want to delete this model?")) {
                $.ajax({
                    url: 'submit_data.php?endpoint=delete_model',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ model_name: modelName }),
                    success: function(response) {
                        console.log('Success:', response);
                        alert('Model deleted successfully');
                        listModels(); // Refresh the model list
                    },
                    error: function(xhr, status, error) {
                        console.error('Error:', xhr.responseText);
                        alert('Error deleting model: ' + xhr.responseText);
                    }
                });
            }
        }

        function listModels() {
            $.ajax({
                url: 'submit_data.php?endpoint=list_models',
                type: 'GET',
                success: function(response) {
                    if (response && response.models && Array.isArray(response.models)) {
                        var select = $('#modelSelect');
                        select.empty();
                        response.models.forEach(function(model) {
                            select.append(
                                $('<option>').val(model).text(model)
                            );
                            select.append(
                                $('<button>').text('Delete').click(function() {
                                    deleteModel(model);
                                })
                            );
                        });
                        select.show();
                    } else {
                        alert('Error: Invalid response from server');
                    }
                },
                error: function(xhr, status, error) {
                    alert('Error fetching model list: ' + error);
                }
            });
        }

        function loadModel() {
    var modelName = $('#modelSelect').val();
    if (!modelName) {
        alert('Please select a model first.');
        return;
    }

    $.ajax({
        url: 'submit_data.php?endpoint=load_model',
        type: 'POST',
        data: JSON.stringify({model_name: modelName}),
        contentType: 'application/json',
        success: function(response) {
            $('.output-area').first().text(JSON.stringify(response, null, 2));
            modelLoaded = true;
        },
        error: function(xhr, status, error) {
            $('.output-area').first().text('Error: ' + xhr.responseText);
            modelLoaded = false;
        }
    });
}

        $('#predictForm').submit(function(e) {
            e.preventDefault();
            if (!modelLoaded) {
                $('#predictionResult').text('Please load a model first.');
                return;
            }

            var sample = [];
            $(this).find('input').each(function() {
                sample.push($(this).val() === '' ? null : parseFloat($(this).val()));
            });

            $.ajax({
                url: 'submit_data.php?endpoint=list_models',
                type: 'GET',
                success: function(response) {
                    var select = $('<select>').attr('id', 'modelSelect');
                    response.models.forEach(function(model) {
                        select.append($('<option>').val(model).text(model));
                    });
                    $('#modelFile').replaceWith(select);
                },
                error: function(xhr, status, error) {
                    console.error('Error fetching model list:', error);
                }
            });
        });

        $(document).on('submit', '.training-form', function(e) {
            e.preventDefault();
            if (!modelLoaded) {
                $(this).siblings('.output-area').text('Please load a model first.');
                return;
            }

            var form = $(this);
            var values = [];
            var filledIndices = [];
            var allInputs = [];

            form.find('input').each(function(index) {
                var value = $(this).val().trim();
                var finalValue;
                if (index === 0) {
                    finalValue = value === '' ? 'Bank' : value;
                } else {
                    if (value === '' || value === '*') {
                        finalValue = Math.floor(Math.random() * 100) + 1;
                    } else {
                        finalValue = parseFloat(value);
                        filledIndices.push(index - 1);
                    }
                }
                values.push(finalValue);
                allInputs.push(finalValue);
            });

            values.shift();

            if (values.length !== 9) {
                form.siblings('.output-area').text('Error: Input data must have exactly 9 values (8 features + 1 label)');
                return;
            }

            $.ajax({
                url: 'submit_data.php?endpoint=improve_model',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    new_data: values,
                    filled_indices: filledIndices,
                    all_inputs: allInputs
                }),
                success: function(response) {
                    form.siblings('.output-area').text(JSON.stringify(response, null, 2));
                },
                error: function(xhr, status, error) {
                    form.siblings('.output-area').text('Error: ' + xhr.responseText);
                }
            });
        });

        function saveImprovedModel() {
            var modelName = $('#modelName').val();

            $.ajax({
                url: 'submit_data.php?endpoint=save_improved_model',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({model_name: modelName}),
                success: function(response) {
                    $('.output-area').last().text(JSON.stringify(response, null, 2));
                    listModels(); // Refresh the model list immediately
                },
                error: function(xhr, status, error) {
                    $('.output-area').last().text('Error: ' + xhr.responseText);
                }
            });
        }

        function checkForModelUpdates() {
            if (localStorage.getItem('modelListUpdated') === 'true') {
                listModels();
                localStorage.removeItem('modelListUpdated');
            }
        }

        setInterval(checkForModelUpdates, 5000); // Check every 5 seconds

        function addCell() {
            var newCell = `
            <div class="cell">
                <form class="training-form">
                    <table class="table table-bordered">
                        <thead class="thead-light">
                            <tr>
                                <th>BANK</th>
                                <th>HVCORNER</th>
                                <th>IO</th>
                                <th>CAP</th>
                                <th>POWERH</th>
                                <th>POWER</th>
                                <th>GROUND</th>
                                <th>PROBE</th>
                                <th>FUSE</th>
                                <th>LABEL</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><input type="text" name="bank" class="form-control"></td>
                                <td><input type="number" name="hvcorner" class="form-control"></td>
                                <td><input type="number" name="io" class="form-control"></td>
                                <td><input type="number" name="cap" class="form-control"></td>
                                <td><input type="number" name="powerh" class="form-control"></td>
                                <td><input type="number" name="power" class="form-control"></td>
                                <td><input type="number" name="ground" class="form-control"></td>
                                <td><input type="number" name="probe" class="form-control"></td>
                                <td><input type="number" name="fuse" class="form-control"></td>
                                <td><input type="number" name="label" class="form-control"></td>
                            </tr>
                        </tbody>
                    </table>
                    <button class="btn btn-success trainbutton" type="submit">Train Model</button>
                </form>
                <div class="output-area mt-2"></div>
            </div>`;
            $('#notebook').append(newCell);
        }
    </script>
</body>
</html>
