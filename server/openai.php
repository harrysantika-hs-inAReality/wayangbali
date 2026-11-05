<?php

declare(strict_types=1);

/** Server-only configuration, with environment variables taking precedence. */
function openaiSetting(array $config, string $name, string $default = ''): string
{
    return trim(getenv($name) ?: ($config[$name] ?? $default));
}

/** @return array{status: int, body: string} */
function openaiRequest(string $key, string $path, array $payload, bool $multipart = false): array
{
    $headers = ['Authorization: Bearer ' . $key];
    if (!$multipart) $headers[] = 'Content-Type: application/json';
    $ch = curl_init('https://api.openai.com/v1/' . $path);
    curl_setopt_array($ch, [
        CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 5, CURLOPT_TIMEOUT => 18,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_POSTFIELDS => $multipart ? $payload : json_encode($payload),
    ]);
    $body = curl_exec($ch);
    $status = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return ['status' => $body === false ? 0 : $status, 'body' => $body === false ? '' : $body];
}

function openaiJson(array $response): array
{
    if ($response['status'] !== 200) {
        throw new RuntimeException(
            $response['status'] === 429 ? 'Kuota tutor sementara penuh. Coba lagi nanti.' : 'Tutor belum dapat terhubung. Coba lagi atau hubungi pengelola.',
            $response['status'] === 429 ? 429 : 502,
        );
    }
    $data = json_decode($response['body'], true);
    if (!is_array($data)) throw new RuntimeException('Jawaban tutor tidak valid. Coba lagi.', 502);
    return $data;
}

/** Audio is validated by tutor.php and uploaded from memory, never a local file. */
function openaiTutor(array $config, string $key, string $prompt, string $message, ?array $audio, bool $speak): array
{
    $transcriptionText = '';
    if ($audio !== null) {
        $extension = ['audio/mp4' => 'mp4', 'audio/webm' => 'webm', 'audio/ogg' => 'ogg'][$audio['mimeType']];
        $model = openaiSetting($config, 'OPENAI_TRANSCRIBE_MODEL', 'whisper-1');
        if ($model === 'gpt-transcribe') $model = 'whisper-1';
        $transcription = openaiJson(openaiRequest($key, 'audio/transcriptions', [
            'model' => $model,
            'file' => new CURLStringFile(base64_decode($audio['data'], true), 'question.' . $extension, $audio['mimeType']),
            'response_format' => 'json',
            'language' => 'id',
        ], true));
        $message = is_string($transcription['text'] ?? null) ? trim($transcription['text']) : '';
        $transcriptionText = $message;
        if ($message === '') return ['question' => '', 'answer' => 'Suara belum terdengar. Silakan rekam ulang pertanyaan Anda tentang wayang Bali.'];
        $message = mb_substr($message, 0, 2000);
    }
    $result = openaiJson(openaiRequest($key, 'responses', [
        'model' => openaiSetting($config, 'OPENAI_MODEL', 'gpt-4.1-mini'),
        'instructions' => $prompt, 'input' => $message, 'store' => false,
        'max_output_tokens' => max(64, min(240, (int) openaiSetting($config, 'OPENAI_MAX_OUTPUT_TOKENS', '180'))),
    ]));
    $answer = '';
    foreach ($result['output'] ?? [] as $item) {
        if (($item['type'] ?? '') !== 'message') continue;
        foreach ($item['content'] ?? [] as $part) {
            if (($part['type'] ?? '') === 'output_text' && is_string($part['text'] ?? null)) $answer .= $part['text'];
        }
    }
    $answer = mb_substr(trim($answer), 0, 800);
    if ($answer === '') throw new RuntimeException('Belum ada jawaban. Coba pertanyaan lain tentang wayang Bali.', 502);
    $response = ['answer' => $answer];
    if ($transcriptionText !== '') {
        $response['question'] = mb_substr($transcriptionText, 0, 300);
    }
    if ($speak) {
        $speech = openaiRequest($key, 'audio/speech', [
            'model' => openaiSetting($config, 'OPENAI_TTS_MODEL', 'gpt-4o-mini-tts'),
            'voice' => openaiSetting($config, 'OPENAI_TTS_VOICE', 'coral'),
            'input' => $answer, 'response_format' => 'mp3',
        ]);
        // A speech failure must not discard an otherwise valid text answer.
        if ($speech['status'] === 200 && $speech['body'] !== '') {
            $response['audio'] = ['mimeType' => 'audio/mpeg', 'data' => base64_encode($speech['body'])];
        }
    }
    return $response;
}
