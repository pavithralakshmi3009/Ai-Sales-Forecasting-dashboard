import { downloadExcel, downloadPDF } from '../api';

export default function TopNav({ title, description }) {
  const handleExcelExport = async () => {
    try {
      const result = await downloadExcel();
      if (!result.ok) {
        console.error('Excel export failed:', result.data?.error);
      }
    } catch (err) {
      console.error('Excel export error:', err);
    }
  };

  const handlePDFExport = async () => {
    try {
      const result = await downloadPDF();
      if (!result.ok) {
        console.error('PDF export failed:', result.data?.error);
      }
    } catch (err) {
      console.error('PDF export error:', err);
    }
  };

  return (
    <header className="top-nav">
      <div className="page-title">
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <div className="export-actions">
        <button
          onClick={handleExcelExport}
          className="btn-export btn-excel"
          id="export-excel-link"
        >
          <i className="fa-solid fa-file-excel" />
          Export Excel
        </button>
        <button
          onClick={handlePDFExport}
          className="btn-export btn-pdf"
          id="export-pdf-link"
        >
          <i className="fa-solid fa-file-pdf" />
          PDF Report
        </button>
      </div>
    </header>
  );
}
