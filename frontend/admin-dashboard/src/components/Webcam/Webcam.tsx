import React, { useRef, useCallback, useState } from 'react';
import Webcam from 'react-webcam';
import { Box, Button, Paper } from '@mui/material';
import { PhotoCamera as PhotoIcon } from '@mui/icons-material';

interface WebcamComponentProps {
  onCapture: (imageSrc: string) => void;
  width?: number;
  height?: number;
  disabled?: boolean;
}

const WebcamComponent: React.FC<WebcamComponentProps> = ({
  onCapture,
  width = 320,
  height = 240,
  disabled = false,
}) => {
  const webcamRef = useRef<Webcam>(null);
  const [isCapturing, setIsCapturing] = useState(false);

  const capture = useCallback(() => {
    if (webcamRef.current && !disabled) {
      setIsCapturing(true);
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        onCapture(imageSrc);
      }
      setTimeout(() => setIsCapturing(false), 500);
    }
  }, [onCapture, disabled]);

  const videoConstraints = {
    width: width,
    height: height,
    facingMode: "user"
  };

  return (
    <Paper sx={{ p: 2, display: 'inline-block' }}>
      <Box sx={{ position: 'relative' }}>
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          width={width}
          height={height}
          videoConstraints={videoConstraints}
        />
        {isCapturing && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Box
              sx={{
                width: 40,
                height: 40,
                border: '4px solid #1976d2',
                borderRadius: '50%',
                borderTop: '4px solid transparent',
                animation: 'spin 1s linear infinite',
                '@keyframes spin': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' },
                },
              }}
            />
          </Box>
        )}
      </Box>
      <Box sx={{ mt: 1, textAlign: 'center' }}>
        <Button
          variant="contained"
          startIcon={<PhotoIcon />}
          onClick={capture}
          disabled={disabled || isCapturing}
          size="small"
        >
          Capture
        </Button>
      </Box>
    </Paper>
  );
};

export default WebcamComponent;
