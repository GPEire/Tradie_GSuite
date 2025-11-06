/**
 * Project Dashboard Component
 * TASK-027: Display all active projects with email activity summary
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Avatar,
  LinearProgress,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Folder as FolderIcon,
  Email as EmailIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  Person as PersonIcon,
  LocationOn as LocationOnIcon,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { apiClient } from '../services/api';
import { useProjectStore } from '../store/projectStore';

interface ProjectSummary {
  id: number;
  project_id: string;
  project_name: string;
  address?: string;
  client_name?: string;
  email_count: number;
  last_email_at?: string;
  status: string;
  needs_review: boolean;
  created_at: string;
}

export const ProjectDashboard: React.FC = () => {
  const { projects, loadProjects, isLoading, error } = useProjectStore();
  const [activitySummary, setActivitySummary] = useState<{
    totalProjects: number;
    activeProjects: number;
    totalEmails: number;
    recentActivity: number;
  } | null>(null);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  useEffect(() => {
    if (projects.length > 0) {
      calculateActivitySummary();
    }
  }, [projects]);

  const calculateActivitySummary = () => {
    const activeProjects = projects.filter((p) => p.status === 'active').length;
    const totalEmails = projects.reduce((sum, p) => sum + (p.email_count || 0), 0);
    const now = new Date();
    const recentActivity = projects.filter((p) => {
      if (!p.last_email_at) return false;
      const lastEmail = new Date(p.last_email_at);
      const hoursDiff = (now.getTime() - lastEmail.getTime()) / (1000 * 60 * 60);
      return hoursDiff < 24; // Emails in last 24 hours
    }).length;

    setActivitySummary({
      totalProjects: projects.length,
      activeProjects,
      totalEmails,
      recentActivity,
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'completed':
        return 'default';
      case 'on_hold':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatLastActivity = (dateString?: string) => {
    if (!dateString) return 'No activity';
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return 'Recently';
    }
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
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  const activeProjects = projects.filter((p) => p.status === 'active');

  return (
    <Box sx={{ padding: 3 }}>
      {/* Summary Cards */}
      {activitySummary && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    <FolderIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4">{activitySummary.totalProjects}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Total Projects
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar sx={{ bgcolor: 'success.main' }}>
                    <TrendingUpIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4">{activitySummary.activeProjects}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Active Projects
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar sx={{ bgcolor: 'info.main' }}>
                    <EmailIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4">{activitySummary.totalEmails}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Total Emails
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar sx={{ bgcolor: 'warning.main' }}>
                    <ScheduleIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h4">{activitySummary.recentActivity}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Recent Activity (24h)
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Projects Grid */}
      <Typography variant="h5" sx={{ mb: 2 }}>
        Active Projects
      </Typography>
      {activeProjects.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center">
              No active projects
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {activeProjects.map((project) => (
            <Grid item xs={12} sm={6} md={4} key={project.project_id}>
              <Card
                sx={{
                  height: '100%',
                  cursor: 'pointer',
                  '&:hover': {
                    boxShadow: 4,
                  },
                }}
                onClick={() => {
                  useProjectStore.getState().selectProject(project.project_id);
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                    <Avatar sx={{ bgcolor: 'primary.light', mr: 2 }}>
                      <FolderIcon />
                    </Avatar>
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="h6" component="h3" noWrap>
                          {project.project_name}
                        </Typography>
                        {project.needs_review && (
                          <Tooltip title="Needs review">
                            <WarningIcon color="warning" fontSize="small" />
                          </Tooltip>
                        )}
                      </Box>
                      <Chip
                        label={project.status}
                        size="small"
                        color={getStatusColor(project.status) as any}
                        sx={{ mb: 1 }}
                      />
                    </Box>
                  </Box>

                  {project.address && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <LocationOnIcon fontSize="small" color="action" />
                      <Typography variant="body2" color="text.secondary" noWrap>
                        {project.address}
                      </Typography>
                    </Box>
                  )}

                  {project.client_name && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <PersonIcon fontSize="small" color="action" />
                      <Typography variant="body2" color="text.secondary">
                        {project.client_name}
                      </Typography>
                    </Box>
                  )}

                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Email Activity
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {project.email_count} emails
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min((project.email_count / 100) * 100, 100)}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>

                  {project.last_email_at && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
                      <ScheduleIcon fontSize="small" color="action" />
                      <Typography variant="caption" color="text.secondary">
                        Last activity: {formatLastActivity(project.last_email_at)}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

