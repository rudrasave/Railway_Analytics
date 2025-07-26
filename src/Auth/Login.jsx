import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { auth } from './firebase';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { Box, TextField, Button, Typography, Paper, InputAdornment, IconButton, Snackbar, Alert } from '@mui/material';
import { motion } from 'framer-motion';
import { Visibility, VisibilityOff } from '@mui/icons-material';

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const navigate = useNavigate();

  const validateEmail = (email) => {
    // Simple email regex
    return /^\S+@\S+\.\S+$/.test(email);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateEmail(email)) {
      setSnackbar({ open: true, message: 'Please enter a valid email!', severity: 'error' });
      return;
    }
    if (!password || password.length < 6) {
      setSnackbar({ open: true, message: 'Password must be at least 6 characters.', severity: 'error' });
      return;
    }
    setLoading(true);
    try {
      await signInWithEmailAndPassword(auth, email, password);
      setSnackbar({ open: true, message: 'Login successful!', severity: 'success' });
      setTimeout(() => navigate('/dashboard'), 1000);
    } catch (error) {
      setSnackbar({ open: true, message: error.message, severity: 'error' });
    }
    setLoading(false);
  };

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      padding: 2
    }}>
      <motion.div 
        initial={{ opacity: 0, y: 20 }} 
        animate={{ opacity: 1, y: 0 }} 
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <Paper elevation={10} sx={{ 
          p: 4, 
          borderRadius: 4, 
          width: '100%',
          maxWidth: 420,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(8px)',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          boxShadow: '0 8px 32px rgba(31, 38, 135, 0.1)'
        }}>
          <Box textAlign="center" mb={3}>
            <Typography variant="h4" fontWeight={600} color="primary">
              Welcome Back
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Sign in to your account
            </Typography>
          </Box>
          <form onSubmit={handleSubmit} autoComplete="off">
            <TextField
              fullWidth
              label="Email"
              variant="outlined"
              placeholder="Enter your email"
              type="email"
              autoComplete="email"
              size="medium"
              sx={{ mb: 2, borderRadius: 2 }}
              value={email}
              onChange={e => setEmail(e.target.value)}
              inputProps={{ maxLength: 100 }}
            />
            <TextField
              fullWidth
              label="Password"
              variant="outlined"
              placeholder="Enter your password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              size="medium"
              sx={{ mb: 1, borderRadius: 2 }}
              value={password}
              onChange={e => setPassword(e.target.value)}
              inputProps={{ maxLength: 100 }}
              InputProps={{
                style: { borderRadius: 12 },
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            <Box textAlign="right" mb={2}>
              <Link to="/forgot-password" style={{ textDecoration: 'none' }}>
                <Typography variant="caption" color="primary">
                  Forgot password?
                </Typography>
              </Link>
            </Box>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              size="large"
              disabled={loading}
              sx={{
                mt: 1,
                mb: 2,
                borderRadius: 12,
                height: 48,
                fontWeight: 600,
                textTransform: 'none',
                boxShadow: 'none',
                '&:hover': {
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                }
              }}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
          <Typography variant="body2" align="center" color="text.secondary" mt={2}>
            Don't have an account?{' '}
            <Link to="/signup" style={{ textDecoration: 'none', fontWeight: 600 }}>
              <Typography component="span" color="primary">
                Create one
              </Typography>
            </Link>
          </Typography>
          <Box mt={3} textAlign="center">
            <Typography variant="caption" color="text.disabled">
              By continuing, you agree to our Terms and Conditions
            </Typography>
          </Box>
        </Paper>
        <Snackbar
          open={snackbar.open}
          autoHideDuration={4000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </motion.div>
    </Box>
  );
};

export default Login; 