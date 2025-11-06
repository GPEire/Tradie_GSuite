/**
 * Client Contact View Component
 * TASK-029: Display extracted client contacts per project
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Typography,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Chip,
  Avatar,
  Divider,
  Paper,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Business as BusinessIcon,
  ContactMail as ContactMailIcon,
  OpenInNew as OpenIcon,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { apiClient } from '../services/api';

interface ClientContact {
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  role?: string;
  email_count?: number;
  last_email_at?: string;
}

interface ClientContactViewProps {
  projectId: string;
}

export const ClientContactView: React.FC<ClientContactViewProps> = ({
  projectId,
}) => {
  const [contacts, setContacts] = useState<ClientContact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [project, setProject] = useState<any>(null);

  useEffect(() => {
    loadContacts();
  }, [projectId]);

  const loadContacts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Get project details which includes client information
      const projectData = await apiClient.getProject(projectId);
      setProject(projectData);

      // Extract contacts from project
      const extractedContacts: ClientContact[] = [];

      // Primary client from project
      if (projectData.client_name || projectData.client_email) {
        extractedContacts.push({
          name: projectData.client_name || 'Unknown',
          email: projectData.client_email,
          phone: projectData.client_phone,
          company: projectData.client_company,
          email_count: projectData.email_count,
          last_email_at: projectData.last_email_at,
        });
      }

      // TODO: Extract additional contacts from project emails
      // This would require backend endpoint to extract all unique senders from project emails

      setContacts(extractedContacts);
    } catch (err: any) {
      setError(err.message || 'Failed to load contacts');
      console.error('Error loading contacts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenEmail = (email: string) => {
    window.open(`mailto:${email}`, '_blank');
  };

  const handleOpenInGmail = (email: string) => {
    window.open(`https://mail.google.com/mail/u/0/#search/from%3A${encodeURIComponent(email)}`, '_blank');
  };

  const getInitials = (name: string) => {
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ padding: 2 }}>
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Box>
    );
  }

  if (contacts.length === 0) {
    return (
      <Box sx={{ padding: 4, textAlign: 'center' }}>
        <ContactMailIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="body1" color="text.secondary">
          No client contacts found for this project
        </Typography>
      </Box>
    );
  }

  return (
    <Paper sx={{ height: '100%', overflow: 'auto' }}>
      <Box sx={{ padding: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Typography variant="h6" component="h2">
          Client Contacts ({contacts.length})
        </Typography>
      </Box>

      <Grid container spacing={2} sx={{ padding: 2 }}>
        {contacts.map((contact, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card
              sx={{
                height: '100%',
                '&:hover': {
                  boxShadow: 4,
                },
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                    {getInitials(contact.name)}
                  </Avatar>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" component="h3" noWrap>
                      {contact.name}
                    </Typography>
                    {contact.role && (
                      <Typography variant="caption" color="text.secondary">
                        {contact.role}
                      </Typography>
                    )}
                  </Box>
                </Box>

                <Divider sx={{ my: 2 }} />

                {contact.email && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <EmailIcon fontSize="small" color="action" />
                    <Typography variant="body2" sx={{ flex: 1 }} noWrap>
                      {contact.email}
                    </Typography>
                    <Box>
                      <Tooltip title="Send email">
                        <IconButton size="small" onClick={() => handleOpenEmail(contact.email!)}>
                          <EmailIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="View in Gmail">
                        <IconButton size="small" onClick={() => handleOpenInGmail(contact.email!)}>
                          <OpenIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                )}

                {contact.phone && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <PhoneIcon fontSize="small" color="action" />
                    <Typography variant="body2">{contact.phone}</Typography>
                  </Box>
                )}

                {contact.company && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <BusinessIcon fontSize="small" color="action" />
                    <Typography variant="body2">{contact.company}</Typography>
                  </Box>
                )}

                {contact.email_count && (
                  <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                    <Typography variant="caption" color="text.secondary">
                      {contact.email_count} email{contact.email_count !== 1 ? 's' : ''} in project
                    </Typography>
                    {contact.last_email_at && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        Last: {formatDistanceToNow(new Date(contact.last_email_at), { addSuffix: true })}
                      </Typography>
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

