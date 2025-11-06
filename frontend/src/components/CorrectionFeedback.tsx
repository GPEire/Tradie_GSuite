/**
 * Correction Feedback Component
 * TASK-032: Capture user corrections and feedback
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  Rating,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Close as CloseIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  Feedback as FeedbackIcon,
} from '@mui/icons-material';
import { apiClient } from '../services/api';

interface CorrectionFeedbackProps {
  open: boolean;
  onClose: () => void;
  correctionType: 'project_assignment' | 'project_merge' | 'project_split' | 'project_rename';
  originalResult: any;
  correctedResult: any;
  emailId?: string;
  projectId?: string;
  onSubmitted?: () => void;
}

export const CorrectionFeedback: React.FC<CorrectionFeedbackProps> = ({
  open,
  onClose,
  correctionType,
  originalResult,
  correctedResult,
  emailId,
  projectId,
  onSubmitted,
}) => {
  const [rating, setRating] = useState<number | null>(null);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      // Record the correction
      await apiClient.recordCorrection({
        correction_type: correctionType,
        original_result: originalResult,
        corrected_result: correctedResult,
        email_id: emailId,
        project_id: projectId,
        correction_reason: comment || undefined,
      });

      // Submit feedback if rating is provided
      if (rating !== null) {
        await apiClient.submitFeedback({
          feedback_type: correctionType,
          rating: rating,
          comment: comment || undefined,
          context: {
            original_result: originalResult,
            corrected_result: correctedResult,
          },
        });
      }

      setSuccess(true);
      
      if (onSubmitted) {
        onSubmitted();
      }

      // Close after delay
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setRating(null);
    setComment('');
    setError(null);
    setSuccess(false);
    onClose();
  };

  const getCorrectionTypeLabel = () => {
    switch (correctionType) {
      case 'project_assignment':
        return 'Project Assignment';
      case 'project_merge':
        return 'Project Merge';
      case 'project_split':
        return 'Project Split';
      case 'project_rename':
        return 'Project Rename';
      default:
        return 'Correction';
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FeedbackIcon />
            <Typography variant="h6">Feedback</Typography>
          </Box>
          <IconButton size="small" onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        {success ? (
          <Alert severity="success">
            Thank you! Your feedback has been recorded and will help improve the AI.
          </Alert>
        ) : (
          <>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Correction Type:
              </Typography>
              <Chip label={getCorrectionTypeLabel()} size="small" />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                How helpful was this correction?
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                <Rating
                  value={rating}
                  onChange={(_, newValue) => setRating(newValue)}
                  size="large"
                />
                {rating !== null && (
                  <Typography variant="body2" color="text.secondary">
                    {rating <= 2 ? 'Needs improvement' : rating <= 4 ? 'Good' : 'Excellent'}
                  </Typography>
                )}
              </Box>
            </Box>

            <TextField
              fullWidth
              multiline
              rows={4}
              label="Additional Comments (Optional)"
              placeholder="Share any feedback about this correction..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              variant="outlined"
              sx={{ mb: 2 }}
            />

            {error && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            <Alert severity="info">
              <Typography variant="caption">
                Your feedback helps improve the AI's project detection accuracy. Thank you for contributing!
              </Typography>
            </Alert>
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={isSubmitting}>
          {success ? 'Close' : 'Skip'}
        </Button>
        {!success && (
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={isSubmitting || rating === null}
            startIcon={<ThumbUpIcon />}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

