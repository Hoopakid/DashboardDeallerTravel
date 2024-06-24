const staff = document.querySelectorAll('.sidebar li')
// const all = document.querySelector('.all')

// let staffData = document.querySelector('input[name="staff"]');
let leaderboardData = document.querySelector('input[name="leaderboard"]');

// staffData = JSON.parse(staffData.value.replace(/'/g, '"'))
leaderboardData = JSON.parse(leaderboardData.value.replace(/'/g, '"'));

console.log(leaderboardData);

staff.forEach(i => {
    i.onclick = () => {
        staff.forEach(i => {
            i.dataset.selected = 'false';
        })
        i.dataset.selected = 'true';
        if (i.dataset.staff === "all") {
            document.querySelector('.all').style.display = 'block';
            document.querySelector('.staff').style.display = 'none';
        } else {
            document.querySelector('.staff h1').textContent = `${i.textContent}ning kunlik hisoboti`
            document.querySelector('.all').style.display = 'none';
            document.querySelector('.staff').style.display = 'flex';
            changeStaffInfo(i.textContent)
        }
    }
})

function changeStaffInfo(staff) {
    let data;
    leaderboardData.forEach(element => {
        if (element.responsible_user === staff) data = element;
        return;
        
        
    });

    document.getElementById('new-leads').textContent = data.new_deals
    document.getElementById('sales-count').textContent = data.sales_count
    document.getElementById('conversion').textContent = data.conversion + "%"
    document.getElementById('active-leads').textContent = data.leads
    document.getElementById('sales-price').textContent = data.sales_price
    // document.getElementById('plan').textContent = "%"
    // document.getElementById('tasks').textContent = "50%"
    // document.getElementById('notes').textContent = "50%"
    // document.getElementById('contact-completion').textContent = "50%"
}
