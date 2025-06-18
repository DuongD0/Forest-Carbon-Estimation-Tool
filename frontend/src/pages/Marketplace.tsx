import React, { useState, useEffect } from 'react';
import { P2PListing } from '../types';
import { getP2PListings } from '../services/p2p';
import P2PListingItem from '../components/P2PListingItem';
import { Container, Grid, Typography, CircularProgress, Alert } from '@mui/material';

const Marketplace = () => {
    const [listings, setListings] = useState<P2PListing[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchListings = async () => {
        try {
            setLoading(true);
            const data = await getP2PListings();
            setListings(data);
            setError(null);
        } catch (err: any) {
            console.error('Error fetching P2P listings:', err);
            console.error('Error details:', {
                message: err.message,
                response: err.response?.data,
                status: err.response?.status
            });
            setError(err.message || 'Failed to fetch P2P listings.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchListings();
    }, []);

    if (loading) {
        return <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Container>;
    }

    if (error) {
        return <Container sx={{ mt: 4 }}><Alert severity="error">{error}</Alert></Container>;
    }

    return (
        <Container sx={{ mt: 4 }}>
            <Typography variant="h4" gutterBottom>
                P2P Marketplace
            </Typography>
            <Grid container spacing={3}>
                {listings.length > 0 ? (
                    listings.map((listing) => (
                        <Grid item key={listing.id} xs={12} sm={6} md={4}>
                            <P2PListingItem listing={listing} onPurchaseSuccess={fetchListings} />
                        </Grid>
                    ))
                ) : (
                    <Typography sx={{ ml: 2, mt: 2 }}>No active listings found.</Typography>
                )}
            </Grid>
        </Container>
    );
};

export default Marketplace; 