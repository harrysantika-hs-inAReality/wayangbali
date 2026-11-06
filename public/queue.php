<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');

const MAX_ACTIVE_DOWNLOADS = 3;
const CLIENT_TTL_SECONDS = 45;

$action = $_GET['action'] ?? 'status';
$client = $_GET['client'] ?? '';
if (!in_array($action, ['join', 'status', 'release'], true) ||
    !preg_match('/^[a-zA-Z0-9-]{16,64}$/', $client)) {
    http_response_code(400);
    echo json_encode(['error' => 'Permintaan antrean tidak valid.']);
    exit;
}

$statePath = sys_get_temp_dir() . '/wayang-download-queue.json';
$lockPath = sys_get_temp_dir() . '/wayang-download-queue.lock';
$lock = fopen($lockPath, 'c+');
if ($lock === false || !flock($lock, LOCK_EX)) {
    http_response_code(503);
    echo json_encode(['error' => 'Antrean sedang tidak tersedia.']);
    exit;
}

$now = microtime(true);
$decoded = is_file($statePath) ? json_decode((string) file_get_contents($statePath), true) : [];
$entries = is_array($decoded) ? $decoded : [];
$entries = array_values(array_filter($entries, static function ($entry) use ($now): bool {
    return is_array($entry) && isset($entry['id'], $entry['seen']) && ($now - (float) $entry['seen']) < CLIENT_TTL_SECONDS;
}));

$index = array_search($client, array_column($entries, 'id'), true);
if ($action === 'release') {
    if ($index !== false) array_splice($entries, (int) $index, 1);
} else {
    if ($index === false) {
        $entries[] = ['id' => $client, 'joined' => $now, 'seen' => $now];
        $index = count($entries) - 1;
    } else {
        $entries[(int) $index]['seen'] = $now;
    }
}

file_put_contents($statePath, json_encode($entries), LOCK_EX);
$index = array_search($client, array_column($entries, 'id'), true);
$position = $index === false ? 0 : ((int) $index + 1);
$reply = [
    'admitted' => $position > 0 && $position <= MAX_ACTIVE_DOWNLOADS,
    'position' => $position,
    'waiting' => max(0, count($entries) - MAX_ACTIVE_DOWNLOADS),
];

flock($lock, LOCK_UN);
fclose($lock);
echo json_encode($reply);
