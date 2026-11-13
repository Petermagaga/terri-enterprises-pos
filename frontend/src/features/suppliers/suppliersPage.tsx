import { useMemo, useState } from 'react'
import type { Supplier } from './supplier.types'
import {
  Users,
  Plus,
  Search,
  ChevronLeft,
  ChevronRight,
  Phone,
  Mail,
  Pencil,
} from 'lucide-react'

import { useSuppliers } from './hooks/useSuppliers'
import SupplierForm from './components/SupplierForm'

export default function SuppliersPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [showSupplierForm, setShowSupplierForm] = useState(false)
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null)

  const { data, isLoading, isError, error } = useSuppliers(page)

  const suppliers = useMemo(
  () => data?.results ?? [],
  [data?.results],
)

  const filteredSuppliers = useMemo(() => {
    const term = search.trim().toLowerCase()

    if (!term) return suppliers

    return suppliers.filter((supplier) =>
      [
        supplier.name,
        supplier.contact_person,
        supplier.phone,
        supplier.email,
      ].some((value) => value.toLowerCase().includes(term)),
    )
  }, [suppliers, search])

  const activeSuppliers = suppliers.filter(
    (supplier) => supplier.is_active,
  ).length

  return (
    <div className="products-page">
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">BUSINESS MANAGEMENT</span>
          <h1>Suppliers</h1>
          <p>Manage your supermarket suppliers and their contact details.</p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() => setShowSupplierForm(true)}
        >
          <Plus size={18} />
          Add Supplier
        </button>
      </div>

      <div className="products-summary">
        <div className="products-summary-card">
          <div className="products-summary-icon">
            <Users size={21} />
          </div>
          <div>
            <span>Suppliers on this page</span>
            <strong>{suppliers.length}</strong>
          </div>
        </div>

        <div className="products-summary-card">
          <div className="products-summary-icon active">
            <Users size={21} />
          </div>
          <div>
            <span>Active on this page</span>
            <strong>{activeSuppliers}</strong>
          </div>
        </div>

        <div className="products-summary-card">
          <div className="products-summary-icon">
            <Users size={21} />
          </div>
          <div>
            <span>Total suppliers</span>
            <strong>{data?.count ?? 0}</strong>
          </div>
        </div>
      </div>

      <div className="products-table-card">
        <div className="products-table-toolbar">
          <div>
            <h2>Supplier Directory</h2>
            <p>Browse your registered suppliers and their contacts.</p>
          </div>

          <div className="products-search">
            <Search size={18} />
            <input
              type="search"
              placeholder="Search suppliers..."
              value={search}
              onChange={(event) => {
                setSearch(event.target.value)
                setPage(1)
              }}
            />
          </div>
        </div>

        {isLoading ? (
          <div className="products-message">
            Loading suppliers...
          </div>
        ) : isError ? (
          <div className="products-message error">
            {error instanceof Error
              ? error.message
              : 'Unable to load suppliers. Please try again.'}
          </div>
        ) : filteredSuppliers.length === 0 ? (
          <div className="products-empty">
            <Users size={38} />
            <h3>
              {search ? 'No matching suppliers' : 'No suppliers yet'}
            </h3>
            <p>
              {search
                ? 'Try another supplier name, contact person or phone number.'
                : 'Register your suppliers to get started with purchasing.'}
            </p>
          </div>
        ) : (
          <div className="products-table-wrapper">
            <table className="products-table">
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Contact Person</th>
                  <th>Phone</th>
                  <th>Email</th>
                  <th>Address</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredSuppliers.map((supplier) => (
                  <tr key={supplier.id}>
                    <td>
                      <strong>{supplier.name}</strong>
                    </td>

                    <td>{supplier.contact_person || '—'}</td>

                    <td>
                      <span className="supplier-contact">
                        <Phone size={14} />
                        {supplier.phone}
                      </span>
                    </td>

                    <td>
                      {supplier.email ? (
                        <span className="supplier-contact">
                          <Mail size={14} />
                          {supplier.email}
                        </span>
                      ) : '—'}
                    </td>

                    <td>{supplier.address || '—'}</td>

                    <td>
                      <span
                        className={`product-status ${
                          supplier.is_active ? 'active' : 'inactive'
                        }`}
                      >
                        {supplier.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>

                  <td>
                    <button
                      type="button"
                      className="icon-button"
                      title="Edit supplier"
                      onClick={() => {
                        setSelectedSupplier(supplier)
                        setShowSupplierForm(true)
                      }}
                    >
                      <Pencil size={16} />
                    </button>
                  </td>

                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="products-pagination">
          <span>
            Showing {suppliers.length === 0 ? 0 : (page - 1) * 20 + 1}
            {' '}to {Math.min(page * 20, data?.count ?? 0)}
            {' '}of {data?.count ?? 0} suppliers
          </span>

          <div>
            <button
              type="button"
              disabled={!data?.previous || isLoading}
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              aria-label="Previous page"
            >
              <ChevronLeft size={18} />
            </button>

            <span>Page {page}</span>

            <button
              type="button"
              disabled={!data?.next || isLoading}
              onClick={() => setPage((current) => current + 1)}
              aria-label="Next page"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </div>


      {showSupplierForm && (
        <SupplierForm
          supplier={selectedSupplier ?? undefined}
          onClose={() => {
            setShowSupplierForm(false)
            setSelectedSupplier(null)
          }}
        />
      )}


    </div>
  )
}