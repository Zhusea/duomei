var vm = new Vue({
    el: '#app',
    data: {
        host,
        username: sessionStorage.username || localStorage.username,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        cart: [],
        total_chioce_count: 0,
        origin_input: 0 // 用于记录手动输入前的值
    },
    computed: {
        total_count: function(){
            var total = 0;
            for(var i=0; i<this.cart.length; i++){
                total += parseInt(this.cart[i].count);
                this.cart[i].amount = (parseFloat(this.cart[i].price) * parseFloat(this.cart[i].count)).toFixed(2);
            }
            return total;
        },
        total_chioce_amount: function(){
            var total = 0;
            this.total_chioce_count = 0;
            for(var i=0; i<this.cart.length; i++){
                if(this.cart[i].chioce) {
                    total += (parseFloat(this.cart[i].price) * parseFloat(this.cart[i].count));
                    this.total_chioce_count += parseInt(this.cart[i].count);
                }
            }
            return total.toFixed(2);
        },
        chioce_all: function(){
            var chioce=true;
            for(var i=0; i<this.cart.length; i++){
                if(this.cart[i].chioce==false){
                    chioce=false;
                    break;
                }
            }
            return chioce;
        }
    },
    mounted: function(){
        // 获取购物车数据
        axios.get(this.host+'/cart/', {
                headers: {
                    'Authorization': 'JWT ' + this.token
                },
                responseType: 'json',
                withCredentials: true
            })
            .then(response => {
                this.cart = response.data;
                for(var i=0; i<this.cart.length; i++){
                    this.cart[i].amount = (parseFloat(this.cart[i].price) * this.cart[i].count).toFixed(2);
                }
            })
            .catch(error => {
                console.log(error.response.data);
            })
    },
    methods: {
        // 退出
        logout: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        // 减少操作
        on_minus: function(index){
            if (this.cart[index].count > 1) {
                var count = this.cart[index].count - 1;
                this.update_count(index, count);
            }
        },
        on_add: function(index){
            var count = this.cart[index].count + 1;
            this.update_count(index, count);
        },
        on_chioce_all: function(){
            var chioce = !this.chioce_all;
            for (var i=0; i<this.cart.length;i++){
                this.cart[i].chioce = chioce;
                this.update_count(i, this.cart[i].count);
            }
        },
         on_input: function(index){
            var val = parseInt(this.cart[index].count);
            if (isNaN(val) || val <= 0) {
                this.cart[index].count = this.origin_input;
            } else {
                // 更新购物车数据
                axios.put(this.host+'/cart/', {
                        sku_id: this.cart[index].id,
                        count: val,
                        chioce: this.cart[index].chioce
                    }, {
                        headers:{
                            'Authorization': 'JWT ' + this.token
                        },
                        responseType: 'json',
                        withCredentials: true
                    })
                    .then(response => {
                        this.cart[index].count = response.data.count;
                    })
                    .catch(error => {
                        if ('non_field_errors' in error.response.data) {
                            alert(error.response.data.non_field_errors[0]);
                        } else {
                            alert('修改购物车失败');
                        }
                        console.log(error.response.data);
                        this.cart[index].count = this.origin_input;
                    })
            }
        },
        // 更新购物车数据
        update_count: function(index, count){
            axios.put(this.host+'/cart/', {
                    sku_id: this.cart[index].id,
                    count,
                    chioce: this.cart[index].chioce
                }, {
                    headers:{
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    this.cart[index].count = response.data.count;
                })
                .catch(error => {
                    if ('non_field_errors' in error.response.data) {
                        alert(error.response.data.non_field_errors[0]);
                    } else {
                        alert('修改购物车失败');
                    }
                    console.log(error.response.data);
                })
        },
        // 更新购物车数据
        update_chioce: function(index) {
            axios.put(this.host+'/cart/', {
                    sku_id: this.cart[index].id,
                    count: this.cart[index].count,
                    chioce: this.cart[index].chioce
                }, {
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    this.cart[index].chioce = response.data.chioce;
                })
                .catch(error => {
                    if ('non_field_errors' in error.response.data) {
                        alert(error.response.data.non_field_errors[0]);
                    } else {
                        alert('修改购物车失败');
                    }
                    console.log(error.response.data);
                })
        },
        // 删除购物车数据
        on_delete: function(index){
            axios.delete(this.host+'/cart/', {
                    data: {
                        sku_id: this.cart[index].id
                    },
                    headers:{
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    this.cart.splice(index, 1);
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },
    }
});
