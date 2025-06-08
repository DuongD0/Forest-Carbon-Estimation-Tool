import React, { useState } from 'react';
import { Modal, Box, Typography, TextField, Button } from '@mui/material';

interface PurchaseModalProps {
    open: boolean;
    onClose: () => void;
    onSubmit: (quantity: number) => void;
    maxQuantity: number;
    pricePerTon: number;
}

const style = {
    position: 'absolute' as 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    border: '2px solid #000',
    boxShadow: 24,
    p: 4,
};

const PurchaseModal: React.FC<PurchaseModalProps> = ({ open, onClose, onSubmit, maxQuantity, pricePerTon }) => {
    const [quantity, setQuantity] = useState<number>(1);
    const [error, setError] = useState<string>('');

    const handleQuantityChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = parseFloat(event.target.value);
        if (value > maxQuantity) {
            setError(`Quantity cannot exceed available amount: ${maxQuantity}`);
        } else if (value < 0) {
            setError('Quantity must be a positive number');
        } else {
            setError('');
        }
        setQuantity(value);
    };

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        if (quantity > 0 && quantity <= maxQuantity) {
            onSubmit(quantity);
        } else {
            setError('Please enter a valid quantity.');
        }
    };

    const totalPrice = (quantity * pricePerTon).toFixed(2);

    return (
        <Modal open={open} onClose={onClose}>
            <Box sx={style} component="form" onSubmit={handleSubmit}>
                <Typography variant="h6" component="h2" gutterBottom>
                    Purchase Carbon Credits
                </Typography>
                <TextField
                    fullWidth
                    margin="normal"
                    type="number"
                    label={`Quantity (Available: ${maxQuantity})`}
                    value={quantity}
                    onChange={handleQuantityChange}
                    error={!!error}
                    helperText={error}
                    inputProps={{ min: 1, max: maxQuantity, step: "0.01" }}
                />
                <Typography variant="body1" sx={{ mt: 2 }}>
                    Total Price: ${totalPrice}
                </Typography>
                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button onClick={onClose} sx={{ mr: 1 }}>Cancel</Button>
                    <Button type="submit" variant="contained" disabled={!!error || quantity <= 0}>
                        Confirm Purchase
                    </Button>
                </Box>
            </Box>
        </Modal>
    );
};

export default PurchaseModal; 