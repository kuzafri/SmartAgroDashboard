<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");
header('Content-Type: application/json');

try {
    $endpoint = isset($_GET['endpoint']) ? $_GET['endpoint'] : null;
    $url = "http://cmp19.pen.efinixinc.com:5001/" . $endpoint;

    if (!$endpoint) {
        throw new Exception('No endpoint specified');
    }

    if ($endpoint == 'list_models') {
        $models_dir = 'models';
        if (!is_dir($models_dir)) {
            echo json_encode(['error' => 'Models directory not found']);
            exit;
        }
        $models = array_filter(scandir($models_dir), function($file) {
            return pathinfo($file, PATHINFO_EXTENSION) === 'pkl';
        });
        $response = ['models' => array_values($models)];
        echo json_encode($response);
        exit;
    }

    if ($endpoint == 'delete_model') {
        $input_data = file_get_contents('php://input');
        $json_data = json_decode($input_data, true);

        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception('Invalid JSON input');
        }

        $model_name = $json_data['model_name'];
        $file_path = 'models/' . $model_name;

        if (file_exists($file_path)) {
            if (unlink($file_path)) {
                echo json_encode(['success' => 'File deleted successfully']);
            } else {
                echo json_encode(['error' => 'Failed to delete file']);
            }
        } else {
            echo json_encode(['error' => 'File not found']);
        }
        exit;
    }

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);

    if ($endpoint == 'load_model') {
        curl_setopt($ch, CURLOPT_POST, true);
        $input_data = file_get_contents('php://input');
        $json_data = json_decode($input_data, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception('Invalid JSON input');
        }
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($json_data));
    } else {
        $input_data = file_get_contents('php://input');
        $json_data = json_decode($input_data, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception('Invalid JSON input');
        }
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($json_data));
    }

    $response = curl_exec($ch);
    if (curl_errno($ch)) {
        throw new Exception(curl_error($ch));
    }
    curl_close($ch);
    echo $response;
} catch (Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
?>