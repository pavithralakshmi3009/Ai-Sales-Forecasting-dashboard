import { useState, useEffect, useRef } from 'react';
import { getSales, addSale, updateSale, deleteSale, uploadCSV } from '../api';
import { useToast } from '../components/Toast';
import SalesModal from '../components/SalesModal';

export default function SalesPage() {
  const { showToast } = useToast();
  const [sales, setSales] = useState([]);
  const [filteredSales, setFilteredSales] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingSale, setEditingSale] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadSales();
  }, []);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredSales(sales);
    } else {
      const q = searchQuery.toLowerCase();
      setFilteredSales(
        sales.filter(
          (s) =>
            s.product.toLowerCase().includes(q) ||
            s.category.toLowerCase().includes(q)
        )
      );
    }
  }, [searchQuery, sales]);

  const loadSales = async () => {
    try {
      const res = await getSales();
      if (res.ok) {
        setSales(res.data);
      } else {
        showToast('Failed to retrieve sales list', 'error');
      }
    } catch {
      showToast('Error connecting to server', 'error');
    }
  };

  const handleSave = async (id, formData) => {
    try {
      let result;
      if (id) {
        result = await updateSale(id, formData);
      } else {
        result = await addSale(formData);
      }

      if (result.ok) {
        showToast(
          id ? 'Sale updated successfully' : 'Sale added successfully',
          'success'
        );
        setModalOpen(false);
        setEditingSale(null);
        loadSales();
      }

      return result;
    } catch {
      return { ok: false, data: { error: 'Error connecting to server' } };
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this sale record?')) return;

    try {
      const result = await deleteSale(id);
      if (result.ok) {
        showToast('Record deleted successfully', 'success');
        loadSales();
      } else {
        showToast(result.data?.error || 'Failed to delete', 'error');
      }
    } catch {
      showToast('Error connecting to server', 'error');
    }
  };

  const handleEdit = (sale) => {
    setEditingSale(sale);
    setModalOpen(true);
  };

  const handleOpenAdd = () => {
    setEditingSale(null);
    setModalOpen(true);
  };

  const handleCSVUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      const result = await uploadCSV(file);
      if (result.ok) {
        showToast(result.data.message, 'success');
      } else {
        showToast(result.data?.error || 'Upload failed', 'error');
      }
    } catch {
      showToast('Error uploading CSV', 'error');
    }

    // Reset the input so re-uploading the same file triggers onChange
    e.target.value = '';
  };

  return (
    <div className="content-section">
      <div className="action-bar">
        <div className="search-box">
          <i className="fa-solid fa-magnifying-glass" />
          <input
            type="text"
            id="sales-search"
            placeholder="Search product name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <input
            type="file"
            accept=".csv"
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={handleCSVUpload}
          />
          <button
            className="btn-upload"
            onClick={() => fileInputRef.current?.click()}
            id="btn-upload-csv"
          >
            <i className="fa-solid fa-cloud-arrow-up" />
            Upload CSV
          </button>

          <button className="btn-primary" onClick={handleOpenAdd} id="btn-open-add-modal">
            <i className="fa-solid fa-plus" />
            Add New Sale
          </button>
        </div>
      </div>

      <div className="glass-card table-card">
        <div className="table-container">
          <table className="main-data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Date</th>
                <th>Product</th>
                <th>Category</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Total</th>
                <th>Profit</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="sales-table-body">
              {filteredSales.length === 0 ? (
                <tr>
                  <td
                    colSpan="9"
                    style={{
                      textAlign: 'center',
                      padding: '30px',
                      color: 'var(--text-muted)',
                    }}
                  >
                    No transaction history found.
                  </td>
                </tr>
              ) : (
                filteredSales.map((s) => (
                  <tr key={s.id}>
                    <td>{s.id}</td>
                    <td>{s.date}</td>
                    <td style={{ fontWeight: 500, color: 'white' }}>{s.product}</td>
                    <td>
                      <span className="badge">{s.category}</span>
                    </td>
                    <td>{s.quantity}</td>
                    <td>₹ {s.price.toFixed(2)}</td>
                    <td style={{ fontWeight: 600, color: 'var(--accent-blue)' }}>
                      ₹ {s.total.toFixed(2)}
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--accent-green)' }}>
                      ₹ {s.profit.toFixed(2)}
                    </td>
                    <td>
                      <button
                        className="btn-action edit-btn"
                        onClick={() => handleEdit(s)}
                        title="Edit"
                      >
                        <i className="fa-solid fa-pen-to-square" />
                      </button>
                      <button
                        className="btn-action delete-btn"
                        onClick={() => handleDelete(s.id)}
                        title="Delete"
                      >
                        <i className="fa-solid fa-trash-can" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <SalesModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingSale(null);
        }}
        onSave={handleSave}
        editSale={editingSale}
      />
    </div>
  );
}
