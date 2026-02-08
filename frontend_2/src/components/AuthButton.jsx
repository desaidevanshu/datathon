import { LogIn, LogOut, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { signInWithGoogle, signOut } from '../services/authService';
import { useState } from 'react';

const AuthButton = () => {
    const { user, anonymousName } = useAuth();
    const [loading, setLoading] = useState(false);

    const handleSignIn = async () => {
        setLoading(true);
        try {
            await signInWithGoogle();
        } catch (error) {
            console.error('Sign in error:', error);
            alert('Failed to sign in. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleSignOut = async () => {
        setLoading(true);
        try {
            await signOut();
        } catch (error) {
            console.error('Sign out error:', error);
            alert('Failed to sign out. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (user) {
        return (
            <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 bg-gray-800 px-3 py-2 rounded-lg">
                    <User className="w-4 h-4 text-cyan-400" />
                    <span className="text-sm text-white">{anonymousName}</span>
                </div>
                <button
                    onClick={handleSignOut}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors disabled:opacity-50"
                >
                    <LogOut className="w-4 h-4" />
                    Sign Out
                </button>
            </div>
        );
    }

    return (
        <button
            onClick={handleSignIn}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors disabled:opacity-50"
        >
            <LogIn className="w-4 h-4" />
            {loading ? 'Signing in...' : 'Sign in with Google'}
        </button>
    );
};

export default AuthButton;
