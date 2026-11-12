---
name: azure-tts
description: Generate standard Mandarin and Thai narration with an existing Azure Speech F0 resource.
---

# Azure Speech F0 text to speech

Use only an existing SpeechServices resource whose SKU was verified as `F0` before synthesis. Do not upgrade the resource or enable a paid service. The Free tier includes 500,000 Neural TTS characters per month; HD voices are outside this path. A batch can cache the verified F0 resource key in process memory after the first check, but never store it on disk.

For Mandarin, `zh-CN-XiaoxiaoNeural` supports `chat-casual`, `chat`, `cheerful`, and other styles. Use SSML `mstts:express-as` for delivery. Start with `chat-casual` for a friendly teaching voice. Use a short sample, then let the user listen before producing the full narration.

For standard Thai pronunciation, `th-TH-PremwadeeNeural` is a standard Neural voice. It has no expressive style, so send plain SSML with `xml:lang="th-TH"`. A change from another Thai voice provider needs user approval before a batch.

The REST endpoint is `https://<region>.tts.speech.microsoft.com/cognitiveservices/v1`, authenticated with the resource key. Send `Content-Type: application/ssml+xml`, `X-Microsoft-OutputFormat: audio-24khz-160kbitrate-mono-mp3`, and a `User-Agent`. Keep keys in memory; never print or save them.

Sources: [pricing](https://azure.microsoft.com/pricing/details/speech/), [REST API](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech), [Chinese voice styles](https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts.)
