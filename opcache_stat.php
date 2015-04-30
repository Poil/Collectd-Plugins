<?php
header('Content-Type: application/json');
//$conf=opcache_get_configuration();
$status=opcache_get_status();
echo json_encode($status,JSON_PRETTY_PRINT);

