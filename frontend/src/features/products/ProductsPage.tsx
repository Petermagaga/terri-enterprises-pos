
import { useMemo, useState } from 'react'
import {
  Package,
  Plus,
  Search,
  ChevronLeft,
  ChevronRight,
  Settings2,
} from 'lucide-react'

import { Link } from 'react-router-dom'

import { useProducts } from './hooks/useProducts'

import ProductForm from './components/ProductForm'

function formatCurrency(value: number | string) {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 2,
  }).format(Number(value))
}

export default function ProductsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [showProductForm, setShowProductForm] = useState(false)
  const { data, isLoading, isError, error } = useProducts(page)

  const products = useMemo(() => data?.results ?? [], [data?.results])

  const filteredProducts = useMemo(() => {
    const term = search.trim().toLowerCase()

    if (!term) return products

    return products.filter((product) =>
      [
        product.name,
        product.sku,
        product.brand,
        product.category.toString(),
      ].some((value) => value.toLowerCase().includes(term)),
    )
  }, [products, search])

  const activeProducts = products.filter(
    (product) => product.is_active,
  ).length

  return (
    <div className="products-page">
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">CATALOGUE MANAGEMENT</span>
          <h1>Products</h1>
          <p>Manage your supermarket products and selling prices.</p>
        </div>
        
        <div className="products-heading-actions">
        <Link to="/catalogue-setup" className="catalogue-setup-button">
            <Settings2 size={18} />
            Catalogue Setup
        </Link>

        <button
            type="button"
            className="primary-button"
            onClick={() => setShowProductForm(true)}
        >
            <Plus size={18} />
            Add Product
        </button>
        </div>

      </div>

      <div className="products-summary">
        <div className="products-summary-card">
          <div className="products-summary-icon">
            <Package size={21} />
          </div>
          <div>
            <span>Products on this page</span>
            <strong>{products.length}</strong>
          </div>
        </div>

        <div className="products-summary-card">
          <div className="products-summary-icon active">
            <Package size={21} />
          </div>
          <div>
            <span>Active on this page</span>
            <strong>{activeProducts}</strong>
          </div>
        </div>

        <div className="products-summary-card">
          <div className="products-summary-icon">
            <Package size={21} />
          </div>
          <div>
            <span>Total products</span>
            <strong>{data?.count ?? 0}</strong>
          </div>
        </div>
      </div>

      <div className="products-table-card">
        <div className="products-table-toolbar">
          <div>
            <h2>Product Catalogue</h2>
            <p>Browse and manage your product records.</p>
          </div>

          <div className="products-search">
            <Search size={18} />
            <input
              type="search"
              placeholder="Search this page..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>
        </div>

        {isLoading ? (
          <div className="products-message">
            Loading products...
          </div>
        ) : isError ? (
          <div className="products-message error">
            {error instanceof Error
              ? error.message
              : 'Unable to load products. Please try again.'}
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="products-empty">
            <Package size={38} />
            <h3>{search ? 'No matching products' : 'No products yet'}</h3>
            <p>
              {search
                ? 'Try another product name, SKU or brand.'
                : 'Add your supermarket products to get started.'}
            </p>
          </div>
        ) : (
          <div className="products-table-wrapper">
            <table className="products-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>SKU</th>
                  <th>Brand</th>
                  <th>Size</th>
                  <th>Retail Price</th>
                  <th>Wholesale Price</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {filteredProducts.map((product) => (
                  <tr key={product.id}>
                    <td>
                      <strong>{product.name}</strong>
                    </td>
                    <td>
                      <span className="product-sku">{product.sku}</span>
                    </td>
                    <td>{product.brand || '—'}</td>
                    <td>
                      {product.size_value} {product.size_unit}
                    </td>
                    <td>{formatCurrency(product.retail_price)}</td>
                    <td>{formatCurrency(product.wholesale_price)}</td>
                    <td>
                      <span
                        className={`product-status ${
                          product.is_active ? 'active' : 'inactive'
                        }`}
                      >
                        {product.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="products-pagination">
          <span>
            Showing {products.length === 0 ? 0 : (page - 1) * 20 + 1}
            {' '}to {Math.min(page * 20, data?.count ?? 0)}
            {' '}of {data?.count ?? 0} products
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

    {showProductForm && (
    <ProductForm onClose={() => setShowProductForm(false)} />
    )}

    </div>
  )
}
