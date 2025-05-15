import React from 'react';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string | string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole 
}) => {
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);

  // Check if user is authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  // If no specific role is required, allow access
  if (!requiredRole) {
    return <>{children}</>;
  }

  // Check if user has the required role
  const requiredRoles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
  const hasRequiredRole = user?.roles.some(role => 
    requiredRoles.includes(role.name)
  );

  if (!hasRequiredRole) {
    // Redirect to dashboard if user doesn't have the required role
    return <Navigate to="/" />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
