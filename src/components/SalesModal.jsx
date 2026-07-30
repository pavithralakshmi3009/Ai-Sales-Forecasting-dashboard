import { useState, useEffect } from 'react';

export default function SalesModal({ isOpen, onClose, onSave, editSale }) {
  const [formData, setFormData] = useState({
    date: '',
    product: '',
    category: '',
    quantity: '',
    price: '',
  });
  const [error, setError] = useState('');

  useEffect(() => {
    if (editSale) {
      setFormData({
        date: editSale.date || '',
        product: editSale.product || '',
        category: editSale.category || '',
        quantity: editSale.quantity || '',
        price: editSale.price || '',
      });
    } else {
      setFormData({
        date: new Date().toISOString().split('T')[0],
        product: '',
        category: '',
        quantity: '',
        price: '',
      });
    }
    setError('');
  }, [editSale, isOpen]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const { date, product, category, quantity, price } = formData;
    if (!date || !product || !category || !quantity || !price) {
      setError('All fields are required');
      return;
    }

    const result = await onSave(
      editSale ? editSale.id : null,
      formData
    );

    if (!result.ok) {
      setError(result.data?.error || 'Submission failed');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{editSale ? 'Edit Sale Record' : 'Add New Sale'}</h3>
          <button type="button" className="btn-close" onClick={onClose} id="btn-close-modal">
            <i className="fa-solid fa-xmark" />
          </button>
        </div>
        <form onSubmit={handleSubmit} id="sales-form">
          <div className="modal-body">
            <div className="input-grid">
              <div className="input-group">
                <label htmlFor="sale-date">Date</label>
                <input
                  type="date"
                  id="sale-date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="input-group">
                <label htmlFor="sale-category">Category</label>
                <input
                  type="text"
                  id="sale-category"
                  name="category"
                  placeholder="e.g. Electronics"
                  value={formData.category}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
            <div className="input-group">
              <label htmlFor="sale-product">Product Name</label>
              <input
                type="text"
                id="sale-product"
                name="product"
                placeholder="e.g. Smart Watch"
                value={formData.product}
                onChange={handleChange}
                required
              />
            </div>
            <div className="input-grid">
              <div className="input-group">
                <label htmlFor="sale-quantity">Quantity</label>
                <input
                  type="number"
                  id="sale-quantity"
                  name="quantity"
                  min="1"
                  placeholder="e.g. 5"
                  value={formData.quantity}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="input-group">
                <label htmlFor="sale-price">Price (₹)</label>
                <input
                  type="number"
                  id="sale-price"
                  name="price"
                  min="0.01"
                  step="0.01"
                  placeholder="e.g. 1999"
                  value={formData.price}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
            {error && <div className="error-msg">{error}</div>}
          </div>
          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" id="btn-submit-modal">
              {editSale ? 'Update Sale' : 'Save Sale'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
