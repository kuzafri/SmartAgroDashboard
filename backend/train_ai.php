<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Model Training</title>
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
        <h3 class="text-center">Interactive Model Training</h3>

        <div class="mb-4">
            <h4>Load CSV</h4>
            <input type="file" id="csvFile" class="form-control-file" accept=".csv">
            <button onclick="loadCSV()" class="btn btn-primary mt-2">Load CSV</button>
        </div>

        <h4>Train Model</h4>
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
            <h4>Save Model</h4>
            <input type="text" id="modelName" class="form-control" placeholder="Enter model name">
            <button onclick="saveModel()" class="btn btn-primary mt-2">Save Model</button>
        </div>
    </div>

    <script>
        function loadCSV() {
            var csvFile = $('#csvFile')[0].files[0];
            var reader = new FileReader();
            reader.onload = function(e) {
                var csvContent = e.target.result;
                var base64Content = btoa(csvContent);

                $.ajax({
                    url: 'submit_data.php?endpoint=load_csv',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ file_content: base64Content }),
                    success: function(response) {
                        console.log("Success:", response);
                        $('.output-area').first().text(JSON.stringify(response, null, 2));
                    },
                    error: function(xhr, status, error) {
                        console.log("Error:", xhr.responseText);
                        $('.output-area').first().text('Error: ' + xhr.responseText);
                    }
                });
            };
            reader.readAsText(csvFile);
        }

        $(document).on('submit', '.training-form', function(e) {
            e.preventDefault();
            var form = $(this);
            var values = [];
            var filledIndices = [];
            var allInputs = [];

            form.find('input').each(function(index) {
                var value = $(this).val().trim();
                var finalValue;
                if (index === 0) { // Bank input
                    finalValue = value === '' ? 'Bank' : value;
                } else {
                    if (value === '' || value === '*') {
                        finalValue = Math.floor(Math.random() * 100) + 1;
                    } else {
                        finalValue = parseFloat(value);
                        filledIndices.push(index - 1); // Adjust index for filledIndices
                    }
                }
                values.push(finalValue);
                allInputs.push(finalValue);
            });


            // Remove the "Bank" value from the input array before sending it to the server
            values.shift();

            // Ensure exactly 9 values (8 features + 1 label) are sent
            if (values.length !== 9) {
                form.siblings('.output-area').text('Error: Please fill all inputs correctly.');
                return;
            }

            $.ajax({
                url: 'submit_data.php?endpoint=train',
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

        function saveModel() {
            var modelName = $('#modelName').val();

            if (!modelName) {
                alert('Please enter a model name');
                return;
            }

            $.ajax({
                url: 'submit_data.php?endpoint=save_model',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ model_name: modelName }),
                success: function(response) {
                    console.log('Success:', response);
                    alert('Model saved successfully');
                },
                error: function(xhr, status, error) {
                    console.error('Error:', xhr.responseText);
                    alert('Error saving model: ' + xhr.responseText);
                }
            });
        }

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
                                <td><input type="number" name="hvcorner" class="form-control" ></td>
                                <td><input type="number" name="io" class="form-control" ></td>
                                <td><input type="number" name="cap" class="form-control" ></td>
                                <td><input type="number" name="powerh" class="form-control" ></td>
                                <td><input type="number" name="power" class="form-control" ></td>
                                <td><input type="number" name="ground" class="form-control" ></td>
                                <td><input type="number" name="probe" class="form-control" ></td>
                                <td><input type="number" name="fuse" class="form-control" ></td>
                                <td><input type="number" name="label" class="form-control" ></td>
                            </tr>
                        </tbody>
                    </table>
                    <button class="btn btn-success trainbutton" type="submit">Train Model</button>
                </form>
                <div class="output-area mt-2"></div>
            </div>
            `;
            $('#notebook').append(newCell);
        }
    </script>
</body>
</html>
