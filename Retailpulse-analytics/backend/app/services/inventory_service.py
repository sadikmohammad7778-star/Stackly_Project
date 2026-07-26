from sqlalchemy import or_, asc, desc
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models.inventory import Inventory
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product
from app.services.audit_service import create_audit_log

from app.utils.inventory_utils import calculate_stock_status
from app.schemas.inventory_schema import (
    AddStockRequest,
    RemoveStockRequest,
    AdjustStockRequest,
)
from app.models.category import Category



class InventoryService:




    @staticmethod
    def get_inventory(
        db: Session,
        company_id: int,
        search: str = None,
        category: int = None,
        brand: str = None,
        status: str = None,
        sort: str = None,
        order: str = "asc",
    ):

        query = (
            db.query(Inventory, Product)
            .join(Product, Inventory.product_id == Product.id)
            .filter(Inventory.company_id == company_id)
        )

        # Search
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%")
                )
            )

        # Category
        if category:
            query = query.filter(Product.category_id == category)

        # Brand
        if brand:
            query = query.filter(Product.brand == brand)

        # Status
        if status:
            query = query.filter(Inventory.stock_status == status)

        # Sorting
        if sort == "product_name":
            query = query.order_by(
                asc(Product.name) if order == "asc" else desc(Product.name)
            )

        elif sort == "current_stock":
            query = query.order_by(
                asc(Inventory.current_stock)
                if order == "asc"
                else desc(Inventory.current_stock)
            )

        elif sort == "recent":
            query = query.order_by(desc(Inventory.updated_at))

        results = query.all()

        inventory_data = []

        for inventory, product in results:

            inventory_data.append(
                {
                    "id": inventory.id,
                    "product": {
                        "id": product.id,
                        "name": product.name,
                        "brand": product.brand,
                        "sku": product.sku,
                    },
                    "current_stock": inventory.current_stock,
                    "available_stock": inventory.available_stock,
                    "reserved_stock": inventory.reserved_stock,
                    "reorder_level": inventory.reorder_level,
                    "stock_status": inventory.stock_status,
                }
            )

            return inventory_data

    @staticmethod
    def add_stock(
        db: Session,
        data: AddStockRequest,
        user_id: int,
    ):

        product = db.query(Product).filter(
            Product.id == data.product_id
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        inventory = db.query(Inventory).filter(
            Inventory.product_id == data.product_id
        ).first()

        if not inventory:

            inventory = Inventory(
                company_id=product.company_id,
                product_id=product.id,
                current_stock=0,
                reserved_stock=0,
                available_stock=0,
                reorder_level=10,
                stock_status="Out of Stock"
            )

            db.add(inventory)
            db.flush()

        previous_quantity = inventory.current_stock

        inventory.current_stock += data.quantity
        inventory.available_stock = (
            inventory.current_stock - inventory.reserved_stock
        )

        inventory.stock_status = calculate_stock_status(
            inventory.available_stock,
            inventory.reorder_level
        )

        movement = InventoryMovement(
            inventory_id=inventory.id,
            movement_type="Stock Addition",
            quantity_changed=data.quantity,
            previous_quantity=previous_quantity,
            updated_quantity=inventory.current_stock,
            reason=data.reason,
            remarks=data.remarks,
            performed_by=user_id,
        )

        db.add(movement)

        db.commit()
        db.refresh(inventory)

        create_audit_log(
            db=db,
            company_id=inventory.company_id,
            user_id=user_id,
            module="Inventory",
            action="STOCK_IN",
            description=f"Added {data.quantity} units to '{product.name}'",
        )
        return {
            "message": "Stock added successfully",
            "inventory": inventory
        }

    @staticmethod
    def remove_stock(
        db: Session,
        data: RemoveStockRequest,
        user_id: int,
    ):

        product = db.query(Product).filter(
            Product.id == data.product_id
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        inventory = db.query(Inventory).filter(
            Inventory.product_id == data.product_id
        ).first()

        if not inventory:
            raise HTTPException(
                status_code=404,
                detail="Inventory not found"
            )

        if data.quantity > inventory.available_stock:
            raise HTTPException(
                status_code=400,
                detail="Insufficient available stock"
            )

        previous_quantity = inventory.current_stock

        inventory.current_stock -= data.quantity
        inventory.available_stock = (
            inventory.current_stock - inventory.reserved_stock
        )

        inventory.stock_status = calculate_stock_status(
            inventory.available_stock,
            inventory.reorder_level
        )

        movement = InventoryMovement(
            inventory_id=inventory.id,
            movement_type="Stock Removal",
            quantity_changed=data.quantity,
            previous_quantity=previous_quantity,
            updated_quantity=inventory.current_stock,
            reason=data.reason,
            remarks=data.remarks,
            performed_by=user_id,
        )

        db.add(movement)

        db.commit()
        db.refresh(inventory)
        create_audit_log(
            db=db,
            company_id=inventory.company_id,
            user_id=user_id,
            module="Inventory",
            action="STOCK_OUT",
            description=f"Removed {data.quantity} units from '{product.name}'",
        )
        return {
            "message": "Stock removed successfully",
            "inventory": inventory
        }

    @staticmethod
    def adjust_stock(
        db: Session,
        data: AdjustStockRequest,
        user_id: int,
    ):

        product = db.query(Product).filter(
            Product.id == data.product_id
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        inventory = db.query(Inventory).filter(
            Inventory.product_id == data.product_id
        ).first()

        if not inventory:
            raise HTTPException(
                status_code=404,
                detail="Inventory not found"
            )

        if data.quantity < 0:
            raise HTTPException(
                status_code=400,
                detail="Stock cannot be negative"
            )

        previous_quantity = inventory.current_stock

        inventory.current_stock = data.quantity
        inventory.available_stock = (
            inventory.current_stock - inventory.reserved_stock
        )

        inventory.stock_status = calculate_stock_status(
            inventory.available_stock,
            inventory.reorder_level
        )

        movement = InventoryMovement(
            inventory_id=inventory.id,
            movement_type="Manual Adjustment",
            quantity_changed=data.quantity,
            previous_quantity=previous_quantity,
            updated_quantity=inventory.current_stock,
            reason=data.reason,
            remarks=data.remarks,
            performed_by=user_id,
        )

        db.add(movement)

        db.commit()
        db.refresh(inventory)

        create_audit_log(
            db=db,
            company_id=inventory.company_id,
            user_id=user_id,
            module="Inventory",
            action="ADJUST",
            description=(
                f"Adjusted stock of '{product.name}' "
                f"from {previous_quantity} to {inventory.current_stock}"
            ),
        )
        return {
            "message": "Stock adjusted successfully",
            "inventory": inventory,
        }

    @staticmethod
    def get_movement_history(db: Session):

        return (
            db.query(InventoryMovement)
            .order_by(InventoryMovement.created_at.desc())
            .all()
        )

    @staticmethod
    def get_dashboard(db: Session):

        inventories = db.query(Inventory).all()

        total_products = len(inventories)

        total_inventory = sum(
            item.current_stock
            for item in inventories
        )

        low_stock = sum(
            1
            for item in inventories
            if item.stock_status == "Low Stock"
        )

        out_of_stock = sum(
            1
            for item in inventories
            if item.stock_status == "Out of Stock"
        )

        return {
            "total_products": total_products,
            "total_inventory_quantity": total_inventory,
            "low_stock_products": low_stock,
            "out_of_stock_products": out_of_stock
        }

    @staticmethod
    def inventory_by_category(db: Session, company_id: int):

        result = (
            db.query(
                Category.name,
                func.sum(Inventory.current_stock).label("total_stock")
            )
            .join(Product, Product.category_id == Category.id)
            .join(Inventory, Inventory.product_id == Product.id)
            .filter(Inventory.company_id == company_id)
            .group_by(Category.name)
            .all()
        )

        return [
            {
                "category": row.name,
                "total_stock": row.total_stock
            }
            for row in result
        ]
    @staticmethod
    def stock_status_distribution(db: Session, company_id: int):

        result = (
            db.query(
                Inventory.stock_status,
                func.count(Inventory.id).label("count")
            )
            .filter(Inventory.company_id == company_id)
            .group_by(Inventory.stock_status)
            .all()
        )

        return [
            {
                "status": row.stock_status,
                "count": row.count
            }
            for row in result
        ]