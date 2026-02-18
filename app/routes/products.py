from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import Product
from app.extensions import db

bp = Blueprint('products', __name__, url_prefix='/products')

def parse_float(value, field_name, default=None, minimum=None):
    if value is None or str(value).strip() == '':
        if default is not None:
            result = float(default)
        else:
            raise ValueError(f"{field_name} is required")
    else:
        try:
            result = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} must be a valid number") from exc

    if minimum is not None and result < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}")
    return result

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        description = request.form.get('description')
        if not name:
            flash('Product name is required.', 'error')
            return redirect(url_for('products.index'))

        try:
            price = parse_float(request.form.get('price', 0), 'Price', default=0.0, minimum=0.0)
            tax_rate = parse_float(request.form.get('tax_rate', 0), 'Tax rate', default=0.0, minimum=0.0)
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('products.index'))
        
        new_product = Product(
            name=name, price=price, description=description, 
            tax_rate=tax_rate, organization_id=current_user.organization_id
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products.index'))
        
    products = Product.query.filter_by(organization_id=current_user.organization_id).all()
    return render_template('products.html', products=products)

@bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete(product_id):
    product = Product.query.get_or_404(product_id)
    if product.organization_id != current_user.organization_id:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('products.index'))
