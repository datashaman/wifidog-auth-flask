/**
 * From https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API/Using_the_Notifications_API
 */
function setupNotifications() {
  if ("Notification" in window) {
    switch (Notification.permission) {
    case 'granted':
        console.log('Notification permission previously granted');
        break;
    case 'denied':
        console.log('Notification permission previously denied');;
        break;
    default:
        Notification.requestPermission(function (permission) {
            switch (permission) {
            case 'granted':
                console.log('Notification permission granted');
                var notification = new Notification('Notifications here will be used to keep you updated');
                break;
            default:
                console.log('Notification permission ' + permission);
            }
        });
    }
  } else {
    console.log('Notification API not supported');
  }
}
