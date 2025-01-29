let donations = [];

// Add a donation to the pending donations list
document.getElementById('add-donation-button').addEventListener('click', () => {
  const donorName = document.getElementById('donor-name').value;
  const foodItem = document.getElementById('food-item').value;
  const quantity = document.getElementById('quantity').value;
  const expiryDate = document.getElementById('expiry-date').value;

  if (!donorName || !foodItem || !quantity || !expiryDate) {
    alert('Please fill out all fields!');
    return;
  }

  const newDonation = {
    id: Date.now().toString(),
    donorName,
    foodItem,
    quantity,
    expiryDate,
    status: 'pending',
  };

  donations.push(newDonation);
  renderDonations();
  resetDonorForm();
});

// Claim a donation
document.getElementById('claim-button').addEventListener('click', () => {
  const claimerName = document.getElementById('claimer-name').value;
  const claimerContact = document.getElementById('claimer-contact').value;

  if (!claimerName || !claimerContact) {
    alert('Please provide your name and contact.');
    return;
  }

  const selectedDonation = document.querySelector('.donation.selected');
  if (!selectedDonation) {
    alert('Please select a donation to claim.');
    return;
  }

  const donationId = selectedDonation.getAttribute('data-id');
  const donation = donations.find(d => d.id === donationId);
  if (!donation) return;

  // Update the status of the selected donation to claimed
  donation.status = 'claimed';
  donation.claimerName = claimerName;
  donation.claimerContact = claimerContact;

  renderDonations();
  resetClaimerForm();
});

// Render the donations (both pending and claimed)
function renderDonations() {
  const pendingList = document.getElementById('pending-list');
  const claimedList = document.getElementById('claimed-list');

  // Clear existing lists
  pendingList.innerHTML = '';
  claimedList.innerHTML = '';

  donations.forEach(donation => {
    const listItem = document.createElement('li');
    listItem.setAttribute('data-id', donation.id);
    listItem.classList.add(donation.status);

    let listContent = `
      <span><strong>Donor:</strong> ${donation.donorName}</span>
      <span><strong>Food:</strong> ${donation.foodItem}</span>
      <span><strong>Quantity:</strong> ${donation.quantity}</span>
      <span><strong>Expiry:</strong> ${donation.expiryDate}</span>
    `;

    if (donation.status === 'pending') {
      listContent += `<button class="claim-button">Claim</button>`;
    } else {
      listContent += `<span class="claimed-status">Claimed by: ${donation.claimerName}</span>`;
    }

    listItem.innerHTML = listContent;

    if (donation.status === 'pending') {
      pendingList.appendChild(listItem);
      const claimButton = listItem.querySelector('.claim-button');
      claimButton.addEventListener('click', () => {
        claimDonation(donation.id);
      });
    } else {
      claimedList.appendChild(listItem);
    }
  });
}

// Claim a donation and move it to the claimed list
function claimDonation(donationId) {
  const donation = donations.find(d => d.id === donationId);
  
  if (!donation) return;

  const claimerName = document.getElementById('claimer-name').value;
  const claimerContact = document.getElementById('claimer-contact').value;

  if (!claimerName || !claimerContact) {
    alert('Please provide your name and contact.');
    return;
  }

  // Update the donation to be claimed
  donation.status = 'claimed';
  donation.claimerName = claimerName;
  donation.claimerContact = claimerContact;

  renderDonations();
  resetClaimerForm();
}

// Reset the donor form
function resetDonorForm() {
  document.getElementById('donor-name').value = '';
  document.getElementById('food-item').value = '';
  document.getElementById('quantity').value = '';
  document.getElementById('expiry-date').value = '';
}

// Reset the claimer form
function resetClaimerForm() {
  document.getElementById('claimer-name').value = '';
  document.getElementById('claimer-contact').value = '';
}

// Initial render
renderDonations();
