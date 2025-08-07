import React from 'react';
import { useAuth } from '../context/AuthContext';

const ProfilePage = () => {
  const { user } = useAuth();

  return (
    <div>
      <h1>Profile Page</h1>
      {user ? (
        <p>Welcome, user with ID: {user.userId}</p>
      ) : (
        <p>Please log in to see your profile.</p>
      )}
    </div>
  );
};

export default ProfilePage;
