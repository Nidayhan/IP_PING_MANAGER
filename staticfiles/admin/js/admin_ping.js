document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.ping-button');

    buttons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const ip = this.getAttribute('data-ip');

            fetch('/ping-ip/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ ips: [ip] })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response Data:', data);  // Yanıtı konsola yazdırın

                const indicator = document.createElement('span');
                indicator.style.marginLeft = '10px';
                indicator.style.display = 'inline-block';
                indicator.style.width = '10px';
                indicator.style.height = '10px';
                indicator.style.borderRadius = '50%';

                // Yanıt formatını kontrol et ve indikatörü ayarla
                if (data.result && data.result[ip]) {
                    if (data.result[ip] === 'Başarılı') {
                        indicator.style.backgroundColor = 'green';
                    } else if (data.result[ip] === 'Başarısız') {
                        indicator.style.backgroundColor = 'red';
                    } else {
                        console.error('Unexpected ping result:', data.result[ip]);
                    }
                } else {
                    console.error('Unexpected response format:', data);
                }

                // Önceki indikatörü kaldır
                const oldIndicator = this.parentElement.nextElementSibling.querySelector('span');
                if (oldIndicator) {
                    oldIndicator.remove();
                }

                // Yeni indikatörü ekle
                this.parentElement.nextElementSibling.appendChild(indicator);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
