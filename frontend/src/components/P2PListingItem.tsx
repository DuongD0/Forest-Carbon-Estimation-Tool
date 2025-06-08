import React, { useState } from 'react';
import { P2PListing } from '../types';
import p2pService from '../services/p2p';
import PurchaseModal from './PurchaseModal';
import { Card, CardContent, Typography, CardActions, Button, Snackbar, Alert } from '@mui/material';

interface P2PListingItemProps {
    listing: P2PListing;
    onPurchaseSuccess: () => void;
}

const P2PListingItem: React.FC<P2PListingItemProps> = ({ listing, onPurchaseSuccess }) => {
    const [modalOpen, setModalOpen] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [snackbar, setSnackbar] = useState<{ open: boolean, message: string, severity: 'success' | 'error' } | null>(null);

    const handlePurchaseClick = () => {
        setModalOpen(true);
    };

    const handleModalClose = () => {
        setModalOpen(false);
    };

    const handlePurchaseSubmit = async (quantity: number) => {
        setIsSubmitting(true);
        try {
            await p2pService.purchaseCredits(listing.id, quantity);
            setSnackbar({ open: true, message: 'Purchase successful!', severity: 'success' });
            onPurchaseSuccess();
        } catch (error: any) {
            setSnackbar({ open: true, message: error.message || 'Purchase failed.', severity: 'error' });
        } finally {
            setIsSubmitting(false);
            setModalOpen(false);
        }
    };

    const handleSnackbarClose = () => {
        setSnackbar(null);
    };

    return (
        <>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                    <Typography gutterBottom variant="h5" component="div">
                        Carbon Credits
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Available: {listing.quantity} tons
                    </Typography>
                    <Typography variant="h6" color="primary" sx={{ mt: 1 }}>
                        ${listing.price_per_ton.toFixed(2)} / ton
                    </Typography>
                     <Typography variant="caption" color="text.secondary">
                        Seller: ...{listing.seller_id.slice(-6)}
                    </Typography>
                </CardContent>
                <CardActions>
                    <Button
                        size="small"
                        variant="contained"
                        onClick={handlePurchaseClick}
                        disabled={isSubmitting || listing.quantity <= 0}
                    >
                        {isSubmitting ? 'Processing...' : 'Purchase'}
                    </Button>
                </CardActions>
            </Card>

            <PurchaseModal
                open={modalOpen}
                onClose={handleModalClose}
                onSubmit={handlePurchaseSubmit}
                maxQuantity={listing.quantity}
                pricePerTon={listing.price_per_ton}
            />

            {snackbar && (
                <Snackbar
                    open={snackbar.open}
                    autoHideDuration={6000}
                    onClose={handleSnackbarClose}
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
                >
                    <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
                        {snackbar.message}
                    </Alert>
                </Snackbar>
            )}
        </>
    );
};

export default P2PListingItem; 