import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  TextField,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  IconButton,
} from '@mui/material';
import {
  CameraAlt as CameraIcon,
  PhotoCamera as PhotoIcon,
  VideoLibrary as VideoIcon,
  Webcam as WebcamIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import Webcam from 'react-webcam';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { faceRecognitionAPI } from '../../services/api';

const FaceRecognition: React.FC = () => {
  const [enrollmentMode, setEnrollmentMode] = useState(false);
  const [verificationMode, setVerificationMode] = useState(false);
  const [selectedImages, setSelectedImages] = useState<string[]>([]);
  const [employeeId, setEmployeeId] = useState('');
  const [webcamRef, setWebcamRef] = useState<Webcam | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [enrollmentTaskId, setEnrollmentTaskId] = useState<string | null>(null);
  
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const enrollmentSteps = ['Left Profile', 'Right Profile', 'Front Face'];

  // Face enrollment mutation
  const enrollMutation = useMutation({
    mutationFn: (data: { employee_id: string; images: string[]; quality_check: boolean }) =>
      faceRecognitionAPI.enrollFace(data),
    onSuccess: (response) => {
      setEnrollmentTaskId(response.data.id);
      setActiveStep(3); // Move to status step
    },
  });

  // Check enrollment status
  const { data: enrollmentStatus } = useQuery({
    queryKey: ['enrollment-status', enrollmentTaskId],
    queryFn: () => faceRecognitionAPI.getEnrollmentStatus(enrollmentTaskId!),
    enabled: !!enrollmentTaskId,
    refetchInterval: 2000,
  });

  // Face verification mutation
  const verifyMutation = useMutation({
    mutationFn: (data: { image: string; camera_id?: string; location?: string }) =>
      faceRecognitionAPI.verifyFace(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attendance-logs'] });
    },
  });

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      const newImages: string[] = [];
      Array.from(files).forEach((file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          if (e.target?.result) {
            newImages.push(e.target.result as string);
            if (newImages.length === files.length) {
              setSelectedImages(prev => [...prev, ...newImages]);
            }
          }
        };
        reader.readAsDataURL(file);
      });
    }
  };

  const capturePhoto = () => {
    if (webcamRef) {
      const imageSrc = webcamRef.getScreenshot();
      if (imageSrc) {
        setCapturedImage(imageSrc);
        if (enrollmentMode && selectedImages.length < 3) {
          setSelectedImages(prev => [...prev, imageSrc]);
          setActiveStep(prev => prev + 1);
        }
      }
    }
  };

  const removeImage = (index: number) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index));
  };

  const handleEnrollment = () => {
    if (selectedImages.length === 3 && employeeId) {
      enrollMutation.mutate({
        employee_id: employeeId,
        images: selectedImages,
        quality_check: true,
      });
    }
  };

  const handleVerification = () => {
    if (capturedImage) {
      verifyMutation.mutate({
        image: capturedImage,
        location: 'Admin Dashboard',
      });
    }
  };

  const resetEnrollment = () => {
    setEnrollmentMode(false);
    setSelectedImages([]);
    setEmployeeId('');
    setActiveStep(0);
    setEnrollmentTaskId(null);
  };

  const resetVerification = () => {
    setVerificationMode(false);
    setCapturedImage(null);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Face Recognition
      </Typography>

      <Grid container spacing={3}>
        {/* Face Enrollment */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Face Enrollment
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Enroll a new user with 3 photos: left profile, right profile, and front face
            </Typography>

            {!enrollmentMode ? (
              <Button
                variant="contained"
                startIcon={<CameraIcon />}
                onClick={() => setEnrollmentMode(true)}
                fullWidth
                sx={{ mt: 2 }}
              >
                Start Enrollment
              </Button>
            ) : (
              <Box>
                <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
                  {enrollmentSteps.map((label) => (
                    <Step key={label}>
                      <StepLabel>{label}</StepLabel>
                    </Step>
                  ))}
                  <Step>
                    <StepLabel>Processing</StepLabel>
                  </Step>
                </Stepper>

                <TextField
                  label="Employee ID"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                  fullWidth
                  sx={{ mb: 2 }}
                />

                {activeStep < 3 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Capture {enrollmentSteps[activeStep]}:
                    </Typography>
                    <Webcam
                      audio={false}
                      ref={setWebcamRef}
                      screenshotFormat="image/jpeg"
                      width={320}
                      height={240}
                    />
                    <Box sx={{ mt: 1 }}>
                      <Button
                        variant="contained"
                        startIcon={<PhotoIcon />}
                        onClick={capturePhoto}
                        disabled={selectedImages.length >= 3}
                      >
                        Capture Photo
                      </Button>
                      <Button
                        variant="outlined"
                        onClick={() => fileInputRef.current?.click()}
                        sx={{ ml: 1 }}
                      >
                        Upload Image
                      </Button>
                    </Box>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      style={{ display: 'none' }}
                    />
                  </Box>
                )}

                {selectedImages.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Captured Images:
                    </Typography>
                    <Grid container spacing={1}>
                      {selectedImages.map((image, index) => (
                        <Grid item xs={4} key={index}>
                          <Card>
                            <CardContent sx={{ p: 1 }}>
                              <img
                                src={image}
                                alt={`Capture ${index + 1}`}
                                style={{ width: '100%', height: '80px', objectFit: 'cover' }}
                              />
                              <IconButton
                                size="small"
                                onClick={() => removeImage(index)}
                                sx={{ position: 'absolute', top: 0, right: 0 }}
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                )}

                {activeStep === 3 && enrollmentStatus && (
                  <Alert severity={enrollmentStatus.data.status === 'completed' ? 'success' : 'info'}>
                    {enrollmentStatus.data.status === 'completed' 
                      ? 'Face enrollment completed successfully!'
                      : `Status: ${enrollmentStatus.data.status}`
                    }
                  </Alert>
                )}

                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleEnrollment}
                    disabled={selectedImages.length !== 3 || !employeeId || enrollMutation.isPending}
                    sx={{ mr: 1 }}
                  >
                    {enrollMutation.isPending ? <CircularProgress size={20} /> : 'Enroll Face'}
                  </Button>
                  <Button variant="outlined" onClick={resetEnrollment}>
                    Cancel
                  </Button>
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Face Verification */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Face Verification
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Verify a person's identity for attendance
            </Typography>

            {!verificationMode ? (
              <Button
                variant="contained"
                startIcon={<WebcamIcon />}
                onClick={() => setVerificationMode(true)}
                fullWidth
                sx={{ mt: 2 }}
              >
                Start Verification
              </Button>
            ) : (
              <Box>
                <Webcam
                  audio={false}
                  ref={setWebcamRef}
                  screenshotFormat="image/jpeg"
                  width={320}
                  height={240}
                />
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<PhotoIcon />}
                    onClick={capturePhoto}
                    sx={{ mr: 1 }}
                  >
                    Capture & Verify
                  </Button>
                  <Button variant="outlined" onClick={resetVerification}>
                    Cancel
                  </Button>
                </Box>

                {capturedImage && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Captured Image:
                    </Typography>
                    <img
                      src={capturedImage}
                      alt="Captured"
                      style={{ width: '100%', maxWidth: '320px', height: 'auto' }}
                    />
                    <Button
                      variant="contained"
                      onClick={handleVerification}
                      disabled={verifyMutation.isPending}
                      fullWidth
                      sx={{ mt: 1 }}
                    >
                      {verifyMutation.isPending ? <CircularProgress size={20} /> : 'Verify Face'}
                    </Button>
                  </Box>
                )}

                {verifyMutation.isSuccess && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    Face verification completed successfully!
                  </Alert>
                )}

                {verifyMutation.isError && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    Face verification failed. Please try again.
                  </Alert>
                )}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FaceRecognition;
