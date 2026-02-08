import {
    collection,
    addDoc,
    query,
    orderBy,
    onSnapshot,
    updateDoc,
    doc,
    arrayUnion,
    arrayRemove,
    serverTimestamp,
    deleteDoc
} from 'firebase/firestore';
import { db } from '../config/firebase';
import { generateAnonymousName } from './authService';

const REPORTS_COLLECTION = 'reports';

/**
 * Create a new report
 * @param {Object} reportData - Report data (title, description, location, category)
 * @param {Object} user - Current user object
 * @returns {Promise<string>} - Document ID
 */
export const createReport = async (reportData, user) => {
    try {
        const report = {
            userId: user.uid,
            userName: generateAnonymousName(user.uid),
            title: reportData.title,
            description: reportData.description,
            location: reportData.location,
            category: reportData.category,
            timestamp: serverTimestamp(),
            thumbsUp: [],
            thumbsDown: [],
            netScore: 0
        };

        const docRef = await addDoc(collection(db, REPORTS_COLLECTION), report);
        return docRef.id;
    } catch (error) {
        console.error('Error creating report:', error);
        throw error;
    }
};

/**
 * Subscribe to real-time reports updates (sorted by netScore)
 * @param {Function} callback - Callback function with reports array
 * @returns {Function} - Unsubscribe function
 */
export const subscribeToReports = (callback) => {
    // Simplified query - only order by netScore to avoid composite index requirement
    const q = query(
        collection(db, REPORTS_COLLECTION),
        orderBy('netScore', 'desc')
    );

    return onSnapshot(q, (snapshot) => {
        const reports = snapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data(),
            // Convert Firestore timestamp to JS Date
            timestamp: doc.data().timestamp?.toDate()
        }));
        callback(reports);
    }, (error) => {
        console.error('Error subscribing to reports:', error);
    });
};

/**
 * Toggle thumbs up on a report
 * @param {string} reportId - Report document ID
 * @param {string} userId - Current user ID
 * @param {boolean} currentlyUpvoted - Whether user has already upvoted
 * @param {boolean} currentlyDownvoted - Whether user has already downvoted
 */
export const toggleThumbsUp = async (reportId, userId, currentlyUpvoted, currentlyDownvoted) => {
    try {
        const reportRef = doc(db, REPORTS_COLLECTION, reportId);

        const updates = {};

        // If user already upvoted, remove the upvote
        if (currentlyUpvoted) {
            updates.thumbsUp = arrayRemove(userId);
            updates.netScore = -1; // Will be incremented
        } else {
            // Add upvote
            updates.thumbsUp = arrayUnion(userId);
            updates.netScore = 1; // Will be incremented

            // If user had downvoted, remove downvote
            if (currentlyDownvoted) {
                updates.thumbsDown = arrayRemove(userId);
                updates.netScore = 2; // Remove downvote (-1) and add upvote (+1) = +2
            }
        }

        await updateDoc(reportRef, updates);
    } catch (error) {
        console.error('Error toggling thumbs up:', error);
        throw error;
    }
};

/**
 * Toggle thumbs down on a report
 * @param {string} reportId - Report document ID
 * @param {string} userId - Current user ID
 * @param {boolean} currentlyUpvoted - Whether user has already upvoted
 * @param {boolean} currentlyDownvoted - Whether user has already downvoted
 */
export const toggleThumbsDown = async (reportId, userId, currentlyUpvoted, currentlyDownvoted) => {
    try {
        const reportRef = doc(db, REPORTS_COLLECTION, reportId);

        const updates = {};

        // If user already downvoted, remove the downvote
        if (currentlyDownvoted) {
            updates.thumbsDown = arrayRemove(userId);
            updates.netScore = 1; // Will be incremented
        } else {
            // Add downvote
            updates.thumbsDown = arrayUnion(userId);
            updates.netScore = -1; // Will be decremented

            // If user had upvoted, remove upvote
            if (currentlyUpvoted) {
                updates.thumbsUp = arrayRemove(userId);
                updates.netScore = -2; // Remove upvote (+1) and add downvote (-1) = -2
            }
        }

        await updateDoc(reportRef, updates);
    } catch (error) {
        console.error('Error toggling thumbs down:', error);
        throw error;
    }
};

/**
 * Delete a report (only by owner)
 * @param {string} reportId - Report document ID
 */
export const deleteReport = async (reportId) => {
    try {
        await deleteDoc(doc(db, REPORTS_COLLECTION, reportId));
    } catch (error) {
        console.error('Error deleting report:', error);
        throw error;
    }
};
