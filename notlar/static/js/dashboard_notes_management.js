document.addEventListener('DOMContentLoaded', function () {
    function getNoteText(date, content, number, color) {
        return `
        <div
            class="flex items-center p-4 mb-4 text-${color}-800 rounded-lg bg-${color}-50 dark:bg-gray-800 dark:text-${color}-400"
            role="alert">
            <svg class="flex-shrink-0 w-4 h-4" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor"
                viewBox="0 0 20 20">
                <path
                    d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z"/>
            </svg>
            <span class="sr-only">Info</span>
            <div class="ms-3 text-sm font-medium">
                ${date}<br>${content}
            </div>
            <button id="note_${number}" type="button"
                class="ms-auto -mx-1.5 -my-1.5 bg-${color}-50 text-${color}-500 rounded-lg focus:ring-2 focus:ring-${color}-400 p-1.5 hover:bg-${color}-200 inline-flex items-center justify-center h-8 w-8 dark:bg-gray-800 dark:text-${color}-400 dark:hover:bg-gray-700"
                data-dismiss-target="#alert-${number}" aria-label="Close">
                <span class="sr-only">Close</span>
                <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
                </svg>
            </button>
        </div>
        `;
    }

    function fetchAndShowNotes(date) {
        fetch(`/get_notes?date=${date}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(notesData => {
                notesListTable.innerHTML = '';

                notesData.forEach(note => {
                    const newDiv = document.createElement('div');
                    newDiv.classList.add('-my-4', 'divide-y', 'divide-gray-200', 'dark:divide-gray-700');

                    newDiv.innerHTML = getNoteText(note.date, note.content, note.number, note.color);
                    notesListTable.appendChild(newDiv);
                });
            })
            .catch(error => {
                console.error('Error fetching notes:', error);
            });
    }

    function createNote(message, date, color) {
        fetch('/create_note', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: message,
                created_at: date,
                color: color,
            }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                fetchAndShowNotes(date);
            })
            .catch(error => {
                console.error('Error creating note:', error);
            });
    }

    function deleteNote(number) {
        fetch(`/delete_note/${number}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data.message);
                const inputElement = document.getElementById('datapicker-input');
                const currentDate = inputElement.placeholder;
                fetchAndShowNotes(currentDate);
            })
            .catch(error => {
                console.error('Error deleting note:', error);
            });
    }

    function getActualDate() {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
        const day = String(today.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    function getDateBySelectedCell(clickedCellObject) {
        const selectedDate = new Date(parseInt(clickedCellObject.dataset.date));
        const year = selectedDate.getFullYear();
        const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
        const day = String(selectedDate.getDate()).padStart(2, '0');
        const formattedDate = `${year}-${month}-${day}`;
        return formattedDate;
    }

    const notesListTable = document.getElementById('notes-list-table');
    const containerSelector = '.datepicker-grid';
    // Event listener for click
    document.body.addEventListener('click', function (event) {
        const clickedCell = event.target.closest(`${containerSelector} .datepicker-cell`);
        const clickedButton = event.target.closest('button[id^="note_"]');

        if (clickedCell && clickedCell.classList.contains('selected')) {
            const dateBySelectedCell = getDateBySelectedCell(clickedCell);
            fetchAndShowNotes(dateBySelectedCell);
            const inputElement = document.getElementById('datapicker-input');
            inputElement.placeholder = dateBySelectedCell;
        } else if (clickedButton) {
            const noteNumber = clickedButton.id.split('_')[1];
            deleteNote(noteNumber);
        }
    });

    let noteColor;

    const noteForm = document.getElementById('noteForm');

    noteForm.addEventListener('click', function (event) {
        const targetId = event.target.id;
        console.log(targetId)
        if (targetId === 'note-color-green') {
            noteColor = 'green';
        } else if (targetId === 'note-color-red') {
            noteColor = 'red';
        } else if (targetId === 'note-color-gray') {
            noteColor = 'gray';
        }
    });

    noteForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const messageTextarea = document.getElementById('message');
        const message = messageTextarea.value.trim();

        const inputElement = document.getElementById('datapicker-input');
        const placeholderContent = inputElement.placeholder;

        if (message !== '') {
            createNote(message, placeholderContent, noteColor);
        }
    });



    const datePickerInput = document.getElementById('datapicker-input');
    const actualDate = getActualDate();

    if (datePickerInput) {
        datePickerInput.placeholder = actualDate;
    }


    fetchAndShowNotes(actualDate);
});
