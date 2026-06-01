from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.document import Document
from app.services.document_processor import DocumentProcessor
import os
from datetime import datetime

documents_bp = Blueprint('documents', __name__)
processor = DocumentProcessor()

@documents_bp.route('/documents')
@login_required
def index():
    documents = Document.query.filter_by(user_id=current_user.id).all()
    return render_template('documents/index.html', documents=documents)

@documents_bp.route('/documents/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and processor.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Create unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            # Save file
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', unique_filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            
            # Get document type
            doc_type = request.form.get('document_type', 'other')
            
            # Create document record
            document = Document(
                user_id=current_user.id,
                filename=filename,
                file_path=filepath,
                document_type=doc_type,
                file_size=os.path.getsize(filepath)
            )
            
            db.session.add(document)
            db.session.commit()
            
            flash('Document uploaded successfully!', 'success')
            return redirect(url_for('documents.index'))
        else:
            flash('File type not allowed', 'error')
    
    return render_template('documents/upload.html')

@documents_bp.route('/documents/<int:id>')
@login_required
def view(id):
    document = Document.query.get_or_404(id)
    
    if document.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('documents.index'))
    
    return render_template('documents/view.html', document=document)

@documents_bp.route('/documents/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    document = Document.query.get_or_404(id)
    
    if document.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('documents.index'))
    
    # Delete file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    db.session.delete(document)
    db.session.commit()
    
    flash('Document deleted successfully', 'success')
    return redirect(url_for('documents.index'))