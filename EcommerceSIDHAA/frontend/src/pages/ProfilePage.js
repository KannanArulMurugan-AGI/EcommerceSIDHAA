import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const ProfilePage = () => {
  const [user, setUser] = useState({ username: '', email: '' });
  const [passwordData, setPasswordData] = useState({ old_password: '', new_password: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Hardcoded user ID for demonstration purposes
  const userId = 1;
  const apiHeaders = { 'x-user-id': userId };

  const fetchUserProfile = useCallback(async () => {
    try {
      const { data } = await axios.get('http://127.0.0.1:5000/profile', { headers: apiHeaders });
      setUser({ username: data.username, email: data.email });
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch user profile.');
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUserProfile();
  }, [fetchUserProfile]);

  const handleProfileChange = (e) => {
    setUser({ ...user, [e.target.name]: e.target.value });
  };

  const handlePasswordChange = (e) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const { data } = await axios.put('http://127.0.0.1:5000/profile', user, { headers: apiHeaders });
      setSuccess(data.message);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update profile.');
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const { data } = await axios.post('http://127.0.0.1:5000/profile/change-password', passwordData, { headers: apiHeaders });
      setSuccess(data.message);
      setPasswordData({ old_password: '', new_password: '' }); // Clear fields
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to change password.');
    }
  };

  if (loading) return <div className="text-center py-10"><h2>Loading Profile...</h2></div>;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Manage Your Profile</h1>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">{error}</div>}
      {success && <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">{success}</div>}

      {/* Update Profile Form */}
      <div className="bg-white p-8 rounded-lg shadow-md mb-8">
        <h2 className="text-2xl font-semibold mb-6">Your Details</h2>
        <form onSubmit={handleProfileSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700">Username</label>
            <input type="text" name="username" id="username" value={user.username} onChange={handleProfileChange} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
            <input type="email" name="email" id="email" value={user.email} onChange={handleProfileChange} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
          </div>
          <div>
            <button type="submit" className="w-full sm:w-auto bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700">Save Changes</button>
          </div>
        </form>
      </div>

      {/* Change Password Form */}
      <div className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-6">Change Password</h2>
        <form onSubmit={handlePasswordSubmit} className="space-y-6">
          <div>
            <label htmlFor="old_password"className="block text-sm font-medium text-gray-700">Old Password</label>
            <input type="password" name="old_password" id="old_password" value={passwordData.old_password} onChange={handlePasswordChange} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
          </div>
          <div>
            <label htmlFor="new_password"className="block text-sm font-medium text-gray-700">New Password</label>
            <input type="password" name="new_password" id="new_password" value={passwordData.new_password} onChange={handlePasswordChange} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
          </div>
          <div>
            <button type="submit" className="w-full sm:w-auto bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700">Update Password</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfilePage;
