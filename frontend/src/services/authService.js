import {
    signInWithPopup,
    signOut as firebaseSignOut,
    onAuthStateChanged
} from 'firebase/auth';
import { auth, googleProvider } from '../config/firebase';

/**
 * Generate a consistent anonymous name from user ID
 * @param {string} uid - Firebase user ID
 * @returns {string} - Anonymous username like "Anonymous User #1234"
 */
export const generateAnonymousName = (uid) => {
    // Create a simple hash from the uid
    let hash = 0;
    for (let i = 0; i < uid.length; i++) {
        hash = ((hash << 5) - hash) + uid.charCodeAt(i);
        hash = hash & hash; // Convert to 32bit integer
    }
    // Take absolute value and get last 4 digits
    const userId = Math.abs(hash) % 10000;
    return `Anonymous User #${userId.toString().padStart(4, '0')}`;
};

/**
 * Sign in with Google popup
 * @returns {Promise<Object>} - User credential
 */
export const signInWithGoogle = async () => {
    try {
        const result = await signInWithPopup(auth, googleProvider);
        return result.user;
    } catch (error) {
        console.error('Error signing in with Google:', error);
        throw error;
    }
};

/**
 * Sign out current user
 * @returns {Promise<void>}
 */
export const signOut = async () => {
    try {
        await firebaseSignOut(auth);
    } catch (error) {
        console.error('Error signing out:', error);
        throw error;
    }
};

/**
 * Get current user
 * @returns {Object|null} - Current user or null
 */
export const getCurrentUser = () => {
    return auth.currentUser;
};

/**
 * Subscribe to auth state changes
 * @param {Function} callback - Callback function with user parameter
 * @returns {Function} - Unsubscribe function
 */
export const onAuthChange = (callback) => {
    return onAuthStateChanged(auth, callback);
};
