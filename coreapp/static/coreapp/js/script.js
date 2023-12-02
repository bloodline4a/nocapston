document.addEventListener('DOMContentLoaded', function() {
    var toggleButtons = document.querySelectorAll('.toggle-button');
    var aframeContainers = document.querySelectorAll('.aframe-container');
    var playButton = document.querySelector('.unt'); // Corrected query selector
    var tooltip = document.getElementById('play-button-tooltip');

    playButton.addEventListener('mouseover', function(event) {
        const rect = playButton.getBoundingClientRect();
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        tooltip.style.left = rect.left + 'px';
        tooltip.style.display = 'block'; // Display the tooltip
    });

    playButton.addEventListener('mouseout', function(event) {
        tooltip.style.display = 'none'; // Hide the tooltip
    });
    var rooms1 = [];
    for (var i = 0; i < 10; i++) {
        rooms1.push(document.getElementById('room' + i));
    }

    // Select all your a-sky elements for the second A-Frame scene
    var rooms2 = [];
    for (var i = 0; i < 9; i++) {
        rooms2.push(document.getElementById('model2-room' + i));
    }
    
    var rooms3 = [];
    for (var i = 0; i < 9; i++) {
        rooms3.push(document.getElementById('model3-room' + i));
    }

    var rooms4 = [];
    for (var i = 0; i < 9; i++) {
        rooms4.push(document.getElementById('model4-room' + i));
    }


    function handleRoomClick(rooms, prefix) {
        rooms.forEach(function(room, index) {
            room.addEventListener('click', function() {
                console.log(prefix + ' Room ' + index + ' clicked');
            });
        });
    }

    // Function to handle keyboard navigation for A-Frame scenes
    function handleKeyboardNavigation(rooms, prefix) {
    window.addEventListener('keydown', function(event) {
        // Check if the pressed key is a number between 1 and 0
        var numberKey = parseInt(event.key);
        if ((numberKey >= 1 && numberKey <= 9) || numberKey === 0) {
            // Extract the room number from the pressed number key
            var roomNumber = numberKey === 0 ? 9 : numberKey - 1; // Handle key '0' as the 10th room

            // Show the clicked room and hide others
            rooms.forEach(function(room, index) {
                room.setAttribute('visible', index === roomNumber);
            });

            // Modify your variables or properties here based on the room number
            console.log(prefix + ' Room ' + (roomNumber + 1) + ' selected');
        }
    });
}
    toggleButtons.forEach(function(button, index) {
        button.addEventListener('click', function() {
            aframeContainers.forEach(function(container) {
                container.style.display = 'none';
            });
            aframeContainers[index].style.display = 'block';

            // Set visibility of corresponding A-Frame scene based on the index
            var scenes = document.querySelectorAll('a-scene');
            scenes.forEach(function(scene, sceneIndex) {
                scene.setAttribute('visible', index === sceneIndex);
            });
        });
    });

    handleRoomClick(rooms1, 'Room 1');
    handleKeyboardNavigation(rooms1, 'Room 1');

    handleRoomClick(rooms2, 'Model 2 Room ');
    handleKeyboardNavigation(rooms2, 'Model 2 Room ');

    handleRoomClick(rooms3, 'Model 3 Room ');
    handleKeyboardNavigation(rooms3, 'Model 3 Room ');

    handleRoomClick(rooms4, 'Model 4 Room ');
    handleKeyboardNavigation(rooms4, 'Model 4 Room ');
});
