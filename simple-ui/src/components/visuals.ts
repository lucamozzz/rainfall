/*
 Copyright (C) 2023 Università degli Studi di Camerino.
 Authors: Alessandro Antinori, Rosario Capparuccia, Riccardo Coltrinari, Flavio Corradini, Marco Piangerelli, Barbara Re, Marco Scarpetta, Luca Mozzoni, Vincenzo Nucci

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

 export const csvToHtmlPage = (csvContent: string, title: string): string => {
    // Split CSV content into rows
    const rows = csvContent.trim().split('\n').slice(0, 100); // Limit to first 100 rows

    // Start with the full HTML structure
    let html = `<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>${title}</title>
      <style>
        table {
          border-collapse: collapse;
          width: 100%;
          margin-top: 20px;
        }
        th, td {
          border: 1px solid black;
          padding: 8px;
          text-align: left;
        }
        th {
          background-color: #f2f2f2;
        }
      </style>
    </head>
    <body>
      <h1>${title}</h1>
      <table>`;

    // Process each row
    rows.forEach((row, rowIndex) => {
        // Check which delimiter to use
        const delimiter = row.includes(',') ? ',' : ';';
        const cells = row.split(delimiter); // Split based on the detected delimiter

        // If it's the first row, treat it as the header
        if (rowIndex === 0) {
            html += '<thead><tr>';
            cells.forEach((cell) => {
                html += `<th>${cell.trim()}</th>`; // Add empty column
            });
            html += '</tr></thead><tbody>';
        } else {
            // Otherwise, treat it as a data row
            html += '<tr>';
            cells.forEach((cell) => {
                html += `<td>${cell.trim()}</td>`; // Add empty column
            });
            html += '</tr>';
        }
    });

    // Close table tags and HTML structure
    html += '</tbody></table></body></html>';

    return html;
};
