document.addEventListener('DOMContentLoaded', function() {
    // Tek tek ping butonları
    const pingButtons = document.querySelectorAll('.ping-button');
    pingButtons.forEach(button => {
        button.addEventListener('click', function() {
            const ipAddress = this.getAttribute('data-ip');
            const row = this.closest('tr');
            const pingStatusSpan = row.querySelector('.ping-status span');

            fetch('/ping-ip/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ ips: [ipAddress] })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);  // Sunucudan gelen yanıtı kontrol edin
                if (data.result[ipAddress] === 'Başarılı') {  // 'result' içinde IP adresini kontrol et
                    pingStatusSpan.textContent = 'Evet';
                    pingStatusSpan.className = 'ping-status ping-yes';
                } else {
                    pingStatusSpan.textContent = 'Hayır';
                    pingStatusSpan.className = 'ping-status ping-no';
                }
            })
            .catch(error => console.error('Ping testi sırasında hata oluştu:', error));
        });
    });

    // Toplu ping atma
    document.getElementById('ping-button').addEventListener('click', async function() {
        const ipAddresses = Array.from(document.querySelectorAll('.ip-address')).map(td => td.textContent.trim());
    
        // Her IP adresine sırasıyla ping atma ve sonucu anında güncelleme
        for (const ip of ipAddresses) {
            const row = document.querySelector(`tr[data-ip="${ip}"]`);
            if (row) {
                const pingStatusSpan = row.querySelector('.ping-status span');
                pingStatusSpan.textContent = 'Yükleniyor...';
                pingStatusSpan.className = 'ping-status ping-loading';
    
                try {
                    const response = await fetch('/check-ip-status/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ ips: [ip] })
                    });
                    const data = await response.json();
    
                    if (data.results[ip] === 'Başarılı') {
                        pingStatusSpan.textContent = 'Evet';
                        pingStatusSpan.className = 'ping-status ping-yes';
                    } else {
                        pingStatusSpan.textContent = 'Hayır';
                        pingStatusSpan.className = 'ping-status ping-no';
                    }
                } catch (error) {
                    console.error(`IP ${ip} için ping testi sırasında hata oluştu:`, error);
                    pingStatusSpan.textContent = 'Hata';
                    pingStatusSpan.className = 'ping-status ping-error';
                }
            }
        }
    });
    
    

    // CSRF token'ını almak için yardımcı fonksiyon
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
