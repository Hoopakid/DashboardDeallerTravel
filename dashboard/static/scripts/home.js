const staff = document.querySelectorAll('.sidebar li')
// const all = document.querySelector('.all')

staff.forEach(i => {
    i.onclick = () => {
        staff.forEach(i => {
            i.dataset.selected = 'false';
        })
        i.dataset.selected = 'true';
        if (i.dataset.staff==="all") {
            document.querySelector('.all').style.display = 'block';
            document.querySelector('.staff').style.display = 'none';
        } else {
            document.querySelector('.staff h1').innerHTML = `${i.innerHTML}ning kunlik hisoboti`
            document.querySelector('.all').style.display = 'none';
            document.querySelector('.staff').style.display = 'flex';
        }
    }
})
