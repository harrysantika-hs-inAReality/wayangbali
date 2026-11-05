`hand_landmarker.task` is Google's HandLandmarker (full), float16 model bundle.

Source: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task

Documentation: https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker

The app serves this file at `models/hand_landmarker.task` relative to Vite's base URL.
If it is missing, download the model from the source above to this directory.
MediaPipe WASM files are copied from the installed package by `npm run dev` and
`npm run build`. No CDN or camera-frame uploads are used at runtime.
