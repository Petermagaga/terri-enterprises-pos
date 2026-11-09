
import { useState } from 'react'
import axios from 'axios'
import { ArrowLeft, Plus, Pencil, Tags, Package } from 'lucide-react'
import { Link } from 'react-router-dom'

import {
  useCategories,
  useProductFamilies,
  useCreateCategory,
  useUpdateCategory,
  useCreateProductFamily,
  useUpdateProductFamily,
} from './hooks/useProducts'

import type {
  Category,
  ProductFamily,
} from './product-catalog.types'

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data

    if (typeof data === 'string') return data

    if (data && typeof data === 'object') {
      return Object.entries(data as Record<string, unknown>)
        .map(([field, messages]) => {
          const message = Array.isArray(messages)
            ? messages.join(', ')
            : String(messages)

          return `${field}: ${message}`
        })
        .join(' ')
    }
  }

  return error instanceof Error
    ? error.message
    : 'Something went wrong. Please try again.'
}

export default function CatalogueSetupPage() {
  const { data: categoriesData, isLoading: categoriesLoading } = useCategories()
  const { data: familiesData, isLoading: familiesLoading } = useProductFamilies()

  const createCategory = useCreateCategory()
  const updateCategory = useUpdateCategory()
  const createFamily = useCreateProductFamily()
  const updateFamily = useUpdateProductFamily()

  const [categoryName, setCategoryName] = useState('')
  const [categoryDescription, setCategoryDescription] = useState('')
  const [categoryActive, setCategoryActive] = useState(true)
  const [editingCategory, setEditingCategory] = useState<Category | null>(null)
  const [categoryError, setCategoryError] = useState('')

  const [familyName, setFamilyName] = useState('')
  const [editingFamily, setEditingFamily] = useState<ProductFamily | null>(null)
  const [familyError, setFamilyError] = useState('')

  const categories = categoriesData?.results ?? []
  const families = familiesData?.results ?? []

  function resetCategoryForm() {
    setCategoryName('')
    setCategoryDescription('')
    setCategoryActive(true)
    setEditingCategory(null)
    setCategoryError('')
  }

  function resetFamilyForm() {
    setFamilyName('')
    setEditingFamily(null)
    setFamilyError('')
  }

  async function handleCategorySubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()
    setCategoryError('')

    const payload = {
      name: categoryName.trim(),
      description: categoryDescription.trim(),
      is_active: categoryActive,
    }

    try {
      if (editingCategory) {
        await updateCategory.mutateAsync({
          id: editingCategory.id,
          payload,
        })
      } else {
        await createCategory.mutateAsync(payload)
      }

      resetCategoryForm()
    } catch (error) {
      setCategoryError(getErrorMessage(error))
    }
  }

  async function handleFamilySubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()
    setFamilyError('')

    const payload = { name: familyName.trim() }

    try {
      if (editingFamily) {
        await updateFamily.mutateAsync({
          id: editingFamily.id,
          payload,
        })
      } else {
        await createFamily.mutateAsync(payload)
      }

      resetFamilyForm()
    } catch (error) {
      setFamilyError(getErrorMessage(error))
    }
  }

  function startEditingCategory(category: Category) {
    setEditingCategory(category)
    setCategoryName(category.name)
    setCategoryDescription(category.description)
    setCategoryActive(category.is_active)
    setCategoryError('')
  }

  function startEditingFamily(family: ProductFamily) {
    setEditingFamily(family)
    setFamilyName(family.name)
    setFamilyError('')
  }

  return (
    <div className="catalogue-page">
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">PRODUCT MANAGEMENT</span>
          <h1>Catalogue Setup</h1>
          <p>Manage product categories and product families.</p>
        </div>

        <Link to="/products" className="catalogue-back-button">
          <ArrowLeft size={17} />
          Back to Products
        </Link>
      </div>

      <div className="catalogue-sections">
        <section className="catalogue-card">
          <div className="catalogue-card-heading">
            <div className="catalogue-icon">
              <Tags size={21} />
            </div>
            <div>
              <h2>Product Categories</h2>
              <p>Group products into supermarket departments.</p>
            </div>
          </div>

          <form onSubmit={handleCategorySubmit} className="catalogue-form">
            <h3>
              {editingCategory ? 'Edit Category' : 'Add New Category'}
            </h3>

            <label>
              Category Name
              <input
                type="text"
                value={categoryName}
                onChange={(event) => setCategoryName(event.target.value)}
                placeholder="e.g. Beverages"
                maxLength={100}
                required
              />
            </label>

            <label>
              Description
              <textarea
                value={categoryDescription}
                onChange={(event) => setCategoryDescription(event.target.value)}
                placeholder="Describe this category..."
                rows={3}
              />
            </label>

            <label className="catalogue-checkbox">
              <input
                type="checkbox"
                checked={categoryActive}
                onChange={(event) => setCategoryActive(event.target.checked)}
              />
              Active category
            </label>

            {categoryError && (
              <p className="catalogue-error">{categoryError}</p>
            )}

            <div className="catalogue-form-actions">
              {editingCategory && (
                <button
                  type="button"
                  className="catalogue-cancel-button"
                  onClick={resetCategoryForm}
                >
                  Cancel
                </button>
              )}

              <button
                type="submit"
                className="primary-button"
                disabled={createCategory.isPending || updateCategory.isPending}
              >
                <Plus size={17} />
                {createCategory.isPending || updateCategory.isPending
                  ? 'Saving...'
                  : editingCategory
                    ? 'Update Category'
                    : 'Add Category'}
              </button>
            </div>
          </form>

          <div className="catalogue-list">
            <div className="catalogue-list-heading">
              <h3>Existing Categories</h3>
              <span>{categories.length}</span>
            </div>

            {categoriesLoading ? (
              <p className="catalogue-empty">Loading categories...</p>
            ) : categories.length === 0 ? (
              <p className="catalogue-empty">No categories created yet.</p>
            ) : (
              categories.map((category) => (
                <div className="catalogue-list-item" key={category.id}>
                  <div>
                    <strong>{category.name}</strong>
                    <span>{category.description || 'No description'}</span>
                    <small className={category.is_active ? 'status-active' : 'status-inactive'}>
                      {category.is_active ? 'Active' : 'Inactive'}
                    </small>
                  </div>

                  <button
                    type="button"
                    className="catalogue-edit-button"
                    onClick={() => startEditingCategory(category)}
                    aria-label={`Edit ${category.name}`}
                  >
                    <Pencil size={16} />
                  </button>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="catalogue-card">
          <div className="catalogue-card-heading">
            <div className="catalogue-icon">
              <Package size={21} />
            </div>
            <div>
              <h2>Product Families</h2>
              <p>Group related products under one brand or family.</p>
            </div>
          </div>

          <form onSubmit={handleFamilySubmit} className="catalogue-form">
            <h3>
              {editingFamily ? 'Edit Product Family' : 'Add New Product Family'}
            </h3>

            <label>
              Family Name
              <input
                type="text"
                value={familyName}
                onChange={(event) => setFamilyName(event.target.value)}
                placeholder="e.g. Coca-Cola"
                maxLength={100}
                required
              />
            </label>

            <p className="catalogue-help">
              The system generates a unique SKU prefix automatically when
              the first product in this family is created.
            </p>

            {familyError && (
              <p className="catalogue-error">{familyError}</p>
            )}

            <div className="catalogue-form-actions">
              {editingFamily && (
                <button
                  type="button"
                  className="catalogue-cancel-button"
                  onClick={resetFamilyForm}
                >
                  Cancel
                </button>
              )}

              <button
                type="submit"
                className="primary-button"
                disabled={createFamily.isPending || updateFamily.isPending}
              >
                <Plus size={17} />
                {createFamily.isPending || updateFamily.isPending
                  ? 'Saving...'
                  : editingFamily
                    ? 'Update Family'
                    : 'Add Family'}
              </button>
            </div>
          </form>

          <div className="catalogue-list">
            <div className="catalogue-list-heading">
              <h3>Existing Product Families</h3>
              <span>{families.length}</span>
            </div>

            {familiesLoading ? (
              <p className="catalogue-empty">Loading product families...</p>
            ) : families.length === 0 ? (
              <p className="catalogue-empty">No product families created yet.</p>
            ) : (
              families.map((family) => (
                <div className="catalogue-list-item" key={family.id}>
                  <div>
                    <strong>{family.name}</strong>
                    <span>
                      SKU Prefix: {family.sku_prefix ?? 'Generated when first product is created'}
                    </span>
                  </div>

                  <button
                    type="button"
                    className="catalogue-edit-button"
                    onClick={() => startEditingFamily(family)}
                    aria-label={`Edit ${family.name}`}
                  >
                    <Pencil size={16} />
                  </button>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
