/**
 * ReuniteAI Photo Upload JS Module
 */

async function uploadPhotoFile(person_id, fileObj) {
  if (!fileObj) return null;

  const allowedExts = ['jpg', 'jpeg', 'png'];
  const ext = fileObj.name.split('.').pop().toLowerCase();
  if (!allowedExts.includes(ext)) {
    Auth.showToast('Invalid photo format. Please upload JPG, JPEG, or PNG.', 'error');
    return null;
  }

  if (fileObj.size > 5 * 1024 * 1024) {
    Auth.showToast('Photo file size exceeds 5MB limit.', 'error');
    return null;
  }

  const formData = new FormData();
  formData.append('photo', fileObj);

  const token = localStorage.getItem('reunite_session_token');
  try {
    const response = await fetch(`/api/persons/${person_id}/photos`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-Session-Token': token
      },
      body: formData
    });

    const data = await response.json();
    if (response.ok && data.success) {
      Auth.showToast('Profile photo uploaded successfully!', 'success');
      return data.data;
    } else {
      Auth.showToast(data.message || 'Photo upload failed.', 'error');
      return null;
    }
  } catch (e) {
    console.error('Photo Upload Exception:', e);
    Auth.showToast('Network error during photo upload.', 'error');
    return null;
  }
}

function handlePhotoSelectPreview(inputElem, previewElemId) {
  const file = inputElem.files[0];
  const preview = document.getElementById(previewElemId);
  if (!preview) return;

  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      preview.src = e.target.result;
      preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }
}
