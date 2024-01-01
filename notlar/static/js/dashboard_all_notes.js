document.addEventListener('DOMContentLoaded', function () {
    const notesListTable = document.getElementById('notes-list-table');
    const startDateInput = document.getElementById('start_datapicker');
    const endDateInput = document.getElementById('end_datapicker');

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

    function fetchAllNotes() {
        fetch('/all_notes', {
            method: 'GET',
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
            .then(allNotesData => {
                renderNotes(allNotesData);
            })
            .catch(error => {
                console.error('Error fetching all notes:', error);
            });
    }

    function fetchNotesByDateRange(start, end) {
        // Format dates 'YYYY-mm-dd'
        const formattedStart = new Date(start).toISOString().split('T')[0];
        const formattedEnd = new Date(end).toISOString().split('T')[0];

        const url = `/all_notes?start=${formattedStart}&end=${formattedEnd}`;

        fetch(url, {
            method: 'GET',
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
            .then(notesData => {
                renderNotes(notesData);
            })
            .catch(error => {
                console.error('Error fetching notes by date range:', error);
            });
    }


    function renderNotes(notesData) {
        notesListTable.innerHTML = '';

        notesData.forEach(note => {
            const newDiv = document.createElement('div');
            newDiv.classList.add('-my-4', 'divide-y', 'divide-gray-200', 'dark:divide-gray-700');
            newDiv.innerHTML = getNoteText(note.date, note.content, note.number, note.color);
            notesListTable.appendChild(newDiv);
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
                fetchAllNotes();
            })
            .catch(error => {
                console.error('Error deleting note:', error);
            });
    }

    fetchAllNotes();

    function handleGlobalClick(event) {
        const clickedButton = event.target.closest('button[id^="note_"]');

        if (clickedButton) {
            const noteNumber = clickedButton.id.split('_')[1];
            console.log(noteNumber)
            deleteNote(noteNumber);
        }

        if (event.target.classList.contains('datepicker-cell')) {
            const selectedDate = new Date(parseInt(event.target.dataset.date, 10));

            if (event.target.classList.contains('range-start')) {
                startDateInput.value = selectedDate.toISOString().split('T')[0];
            } else if (event.target.classList.contains('range-end')) {
                endDateInput.value = selectedDate.toISOString().split('T')[0];
            }


            const start = startDateInput.value;
            const end = endDateInput.value;

            if (start && end) {
                fetchNotesByDateRange(start, end);
            }
        }
    }
    document.addEventListener('click', handleGlobalClick);
});
