import { P2PListing, Transaction } from '../types';
import { api } from './api';

export const getP2PListings = async (): Promise<P2PListing[]> => {
  const response = await api.get('/p2p/listings');
  return response.data;
};

export const purchaseCredits = async (listingId: string, quantity: number): Promise<Transaction> => {
  const response = await api.post(`/p2p/listings/${listingId}/purchase`, { quantity });
  return response.data;
}; 