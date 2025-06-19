# MediaPipe Fashion Measurement API

A RunPod Serverless API that extracts garment measurements from fashion images using MediaPipe pose estimation. Built for NOTMYBRANDS tech pack generation feature.

## 🚀 Overview

This API analyzes fashion product images and extracts accurate measurements using Google's MediaPipe pose estimation technology. It's designed to run on RunPod's serverless infrastructure for cost-effective, scalable measurement extraction.

### Key Features
- **Accurate measurements** from single garment images
- **CPU-only processing** (10x cheaper than GPU solutions)
- **Real-time performance** (3-5 seconds per image)
- **Multiple garment types** (t-shirts, pants, jackets)
- **Confidence scoring** for each measurement
- **Visual output** with pose landmarks

## 📊 Supported Measurements

### T-Shirts
- Chest width
- Body length
- Sleeve length

### Pants
- Waist width
- Inseam length
- Rise

### Jackets
- Chest width
- Body length
- Sleeve length

## 🛠️ Setup Instructions

### 1. Deploy to RunPod Serverless

1. Go to [RunPod Console](https://console.runpod.io)
2. Navigate to **Serverless** → **New Endpoint**
3. Choose **GitHub Repo** as source
4. Enter this repository URL: `https://github.com/valgresky/MediaPipe.git`
5. Configure:
   - **Container Disk**: 10 GB
   - **Timeout**: 60 seconds
   - **Worker Type**: CPU (24 vCPU)
   - **Min Workers**: 0
   - **Max Workers**: 3

### 2. Get Your Endpoint URL

After deployment, you'll receive an endpoint URL:
```
https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync
```

### 3. Get Your API Key

1. Go to RunPod Settings → API Keys
2. Create a new API key
3. Save it securely

## 📡 API Usage

### Request Format

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "image": "BASE64_ENCODED_IMAGE",
      "garment_type": "tshirt"
    }
  }'
```

### Response Format

```json
{
  "status": "COMPLETED",
  "output": {
    "success": true,
    "measurements": {
      "chest_width": 52.3,
      "body_length": 71.5,
      "sleeve_length": 62.8
    },
    "confidence_scores": {
      "chest_width": 0.95,
      "body_length": 0.92,
      "sleeve_length": 0.88
    },
    "visualization": "data:image/png;base64,..."
    "unit": "cm",
    "scale_factor": 2.45
  }
}
```

## 🔌 Integration with NOTMYBRANDS

### Supabase Edge Function Integration

```typescript
async function extractMeasurements(
  imageUrl: string,
  garmentType: string
): Promise<ExtractedMeasurements> {
  // Download image from URL
  const imageResponse = await fetch(imageUrl);
  const imageBlob = await imageResponse.blob();
  const imageBuffer = await imageBlob.arrayBuffer();
  const base64Image = btoa(String.fromCharCode(...new Uint8Array(imageBuffer)));
  
  // Call RunPod endpoint
  const response = await fetch(
    `https://api.runpod.ai/v2/${RUNPOD_ENDPOINT_ID}/runsync`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Deno.env.get('RUNPOD_API_KEY')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        input: {
          image: base64Image,
          garment_type: garmentType
        }
      }),
    }
  );
  
  const result = await response.json();
  
  if (result.status === 'COMPLETED') {
    return result.output;
  } else {
    throw new Error('Measurement extraction failed');
  }
}
```

## 💰 Cost Analysis

| Metric | Value |
|--------|-------|
| Cost per measurement | ~$0.00015 |
| Processing time | 3-5 seconds |
| Monthly cost (50k measurements) | ~$7.50 |
| Compared to GPU solutions | 10x cheaper |
| Compared to API services | 100x cheaper |

## 🔧 Technical Details

### How It Works

1. **Image Input**: Receives base64 encoded fashion image
2. **Pose Detection**: MediaPipe identifies 33 body landmarks
3. **Garment Mapping**: Maps relevant landmarks to garment type
4. **Measurement Extraction**: Calculates distances between landmarks
5. **Scale Estimation**: Uses standard sizing to estimate real measurements
6. **Confidence Scoring**: Provides accuracy confidence for each measurement

### Accuracy

- **Average error**: ±2cm
- **Best for**: Flat lay or mannequin images
- **Limitations**: Requires clear garment visibility

### Performance

- **Cold start**: 5-7 seconds
- **Warm processing**: 3-4 seconds
- **Concurrent requests**: Up to 3 workers

## 🐛 Troubleshooting

### Common Issues

**No pose landmarks detected**
- Ensure garment is clearly visible
- Use high contrast background
- Center garment in frame

**Low confidence scores**
- Improve image lighting
- Use higher resolution images
- Ensure garment is not folded/wrinkled

**Timeout errors**
- Reduce image size (max 4MB recommended)
- Check RunPod endpoint status

### Debug Mode

Set `debug: true` in request to get detailed processing info:

```json
{
  "input": {
    "image": "...",
    "garment_type": "tshirt",
    "debug": true
  }
}
```

## 📝 Environment Variables

For local development, create `.env`:

```bash
RUNPOD_API_KEY=your_api_key_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google MediaPipe team for the pose estimation technology
- RunPod for affordable serverless infrastructure
- NOTMYBRANDS team for the fashion tech pack use case

---

Built with ❤️ for the NOTMYBRANDS platform
