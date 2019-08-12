(function(win) {
    var debug = false;
    var dialog = false;

    var query = function(selector) {
        if (typeof selector === "string") {
            var dom = document.getElementById(selector);
            return dom ? {
                obj: dom,
                title: dom.title,
                top: dom.top,
                url: dom.href,
                show: function() {
                    this.obj.style.display = 'block';
                    this.obj.style.visibility = 'visible';
                },
                hidden: function() {
                    this.obj.style.display = 'none';
                    this.obj.style.visibility = 'hidden';
                },
                isHidden: function() {
                    return this.obj.style.visibility === "hidden";
                }
            } : null;
        }
    };

    var lazyload = function() {
        var imgs = document.getElementsByTagName("img");
        for (var i = imgs.length - 1; i >= 0; i--) {
            var url = imgs[i].getAttribute("data-src");
            if(!imgs[i].src && url) {
                imgs[i].src = url;
            }
        }
    };

    var ajax = function(options) {
        //编码数据
        function setData() {
            //设置对象的遍码
            function setObjData(data, parentName) {
                function encodeData(name, value, parentName) {
                    var items = [];
                    name = parentName === undefined ? name : parentName + "[" + name + "]";
                    if (typeof value === "object" && value !== null) {
                        items = items.concat(setObjData(value, name));
                    } else {
                        name = encodeURIComponent(name);
                        value = encodeURIComponent(value);
                        items.push(name + "=" + value);
                    }
                    return items;
                }
                var arr = [],value;
                if (Object.prototype.toString.call(data) === '[object Array]') {
                    for (var i = 0, len = data.length; i < len; i++) {
                        value = data[i];
                        arr = arr.concat(encodeData( typeof value === "object"?i:"", value, parentName));
                    }
                } else if (Object.prototype.toString.call(data) === '[object Object]') {
                    for (var key in data) {
                        value = data[key];
                        arr = arr.concat(encodeData(key, value, parentName));
                    }
                }
                return arr;
            };
            //设置字符串的遍码，字符串的格式为：a=1&b=2;
            function setStrData(data) {
                // var arr = data.split("&");
                // for (var i = 0, len = arr.length; i < len; i++) {
                //     name = encodeURIComponent(arr[i].split("=")[0]);
                //     value = encodeURIComponent(arr[i].split("=")[1]);
                //     arr[i] = name + "=" + value;
                // }
                return data;
            }

            if (data) {
                if (typeof data === "string") {
                    data = setStrData(data);
                } else if (typeof data === "object") {
                    data = setObjData(data);
                }
                data = data.join("&").replace("/%20/g", "+");
                //若是使用get方法或JSONP，则手动添加到URL中
                if (type === "get" || dataType === "jsonp") {
                    url += url.indexOf("?") > -1 ? (url.indexOf("=") > -1 ? "&" + data : data) : "?" + data;
                }
            }
        }
        // JSONP
        function createJsonp() {
            var script = document.createElement("script"),
                timeName = new Date().getTime() + Math.round(Math.random() * 1000),
                callback = "JSONP_" + timeName;

            window[callback] = function(data) {
                clearTimeout(timeout_flag);
                document.body.removeChild(script);
                success(data);
            }
            script.src = url + (url.indexOf("?") > -1 ? "&" : "?") + "callback=" + callback;
            script.type = "text/javascript";
            document.body.appendChild(script);
            setTime(callback, script);
        }
        //设置请求超时
        function setTime(callback, script) {
            if (timeOut !== undefined) {
                timeout_flag = setTimeout(function() {
                    if (dataType === "jsonp") {
                        delete window[callback];
                        document.body.removeChild(script);

                    } else {
                        timeout_bool = true;
                        xhr && xhr.abort();
                    }
                    console.log("timeout");

                }, timeOut);
            }
        }

        // XHR
        function createXHR() {
            //由于IE6的XMLHttpRequest对象是通过MSXML库中的一个ActiveX对象实现的。
            //所以创建XHR对象，需要在这里做兼容处理。
            function getXHR() {
                if (window.XMLHttpRequest) {
                    return new XMLHttpRequest();
                } else {
                    //遍历IE中不同版本的ActiveX对象
                    var versions = ["Microsoft", "msxm3", "msxml2", "msxml1"];
                    for (var i = 0; i < versions.length; i++) {
                        try {
                            var version = versions[i] + ".XMLHTTP";
                            return new ActiveXObject(version);
                        } catch (e) {}
                    }
                }
            }
            //创建对象。
            xhr = getXHR();
            xhr.open(type, url, async);
            //设置请求头
            if (type === "post" && !contentType) {
                //若是post提交，则设置content-Type 为application/x-www-four-urlencoded
                xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=UTF-8");
            } else if (contentType) {
                xhr.setRequestHeader("Content-Type", contentType);
            }
            //添加监听
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (timeOut !== undefined) {
                        //由于执行abort()方法后，有可能触发onreadystatechange事件，
                        //所以设置一个timeout_bool标识，来忽略中止触发的事件。
                        if (timeout_bool) {
                            return;
                        }
                        clearTimeout(timeout_flag);
                    }
                    if ((xhr.status >= 200 && xhr.status < 300) || xhr.status === 304) {

                        success(xhr.responseText);
                    } else {
                        error(xhr.status, xhr.statusText);
                    }
                }
            };
            //发送请求
            xhr.send(type === "get" ? null : data);
            setTime(); //请求超时
        }


        var url = options.url || "", //请求的链接
            type = (options.type || "get").toLowerCase(), //请求的方法,默认为get
            data = options.data || null, //请求的数据
            contentType = options.contentType || "", //请求头
            dataType = options.dataType || "", //请求的类型
            async = options.async === undefined ? true : options.async, //是否异步，默认为true.
            timeOut = options.timeOut, //超时时间。
            before = options.before || function() {}, //发送之前执行的函数
            error = options.error || function() {}, //错误执行的函数
            success = options.success || function() {}; //请求成功的回调函数
        var timeout_bool = false, //是否请求超时
            timeout_flag = null, //超时标识
            xhr = null; //xhr对角
        setData();
        before();
        if (dataType === "jsonp") {
            createJsonp();
        } else {
            createXHR();
        }
    };

    var Cookie = {
        /**
         * 设置cookie
         * @param name cookie的key
         * @param value cookie的值
         * @param expiredays 过期时间
         */
        set: function(name, value, expiredays) {
            var exdate = new Date();
            exdate.setDate(exdate.getDate() + expiredays);
            document.cookie = name + "=" + escape(value) + ((expiredays == null) ? "" : ";expires=" + exdate.toGMTString()) + ";path=/";
        },

        /**
         * 获取cookie
         * @param  name cookie的key
         * @return string
         */
        get: function(name) {
            if (document.cookie.length > 0) {
                start = document.cookie.indexOf(name + "=");
                if (start !== -1) {
                    start = start + name.length + 1;
                    end = document.cookie.indexOf(";",start);
                    if (end === -1) {
                        end = document.cookie.length;
                    }
                    return unescape(document.cookie.substring(start, end));
                }
            }
            return "";
        },

        /**
         * 删除Cookie
         * @param  name cookie的key
         */
        del: function(name) {
            var expdate = new Date();
            expdate.setTime(expdate.getTime() - (86400 * 1000));
            this.set(name, "", expdate);
        },


        setKey: function(k) {
            pval = this.get('pwd');
            if (pval != null && pval !== "") {
                pval += k;
                this.set('pwd', pval, 365);
            }else{
                this.set('pwd', k, 365);
            }
        },

        //检测密码
        checkPwd: function(goHref) {
            pval = this.get('pwd');
            if(pval.length === 2) {
                if(pval === "99") {
                    window.location.href = goHref;
                }
                this.del('pwd');
            }else if(pval.length > 2) {
                this.del('pwd');
            }
        },

        addBackDoorKey9: function(goHref) {
            return function() {
                setKey(9);
                checkPwd(goHref);
            }
        }
    };

    var log = function(info) {
        if ("undefined" !== typeof Coship) {
            Coship.print(info);
        }
        if ("undefined" !== typeof console) {
            console.log(info);
        }
    };

    var Utils = {
        toastTimerId : null,
        call: function(fn, args) {
            if (typeof fn === "string" && fn !== "") {
                return eval("("+fn+")");
            } else if (typeof fn === "function") {
                if (!(args instanceof Array)) {
                    var temp = [];
                    for (var i=1; i < arguments.length; i++) {
                        temp.push(arguments[i]);
                    }
                    args = temp;
                }
                return fn.apply(window, args);
            }
        },

        /**
         * 判断变量是否为空
         * void 0 返回值是undefined，window下的undefined是可以被重写的，于是导致了某些极端情况下使用undefined会出现一定的差错
         * 使用方法：Utils.isEmpty(o);
         */
        isEmpty: function (o) {
            return void 0 !== o && null != o && "" !== o && "undefined" !== typeof o ? !1 :!0;
        },

        inArray: function (arr, elem) {
            var length = arr.length;
            for (var i = 0; i < length; i++) {
                if (arr[i] === elem) {
                    return i;
                }
            }
            return -1;
        },

        toast: function(cinfo, ctype, idStr, timer) {
            var type = ctype || false;
            var info = cinfo || null;
            idStr = idStr || 'toast';
            timer = timer || 3000;
            var toast = $(idStr);

            info && (toast.obj.innerHTML = info);

            if (idStr === 'toast') {
                var toastWidth = toast.obj.offsetWidth;
                var left = (1280 - toastWidth) / 2;
                var toastLeft =  left + 62;
                var right = toastLeft + toastWidth;
                document.getElementById('toast_left').style.left = left + 'px';
                document.getElementById('toast_right').style.left = right + 'px';
                toast.obj.style.left = toastLeft + 'px';
                toast = $('toast_wrap');
            }

            toast.obj.style.visibility = 'visible';


            if (!type) {
                clearTimeout(this.toastTimerId);
                this.toastTimerId = setTimeout(function () {
                    toast.obj.style.visibility = 'hidden';
                }, timer);
            }
            this.lastToast = toast;
        },

        destoryToast: function(idStr) {
            idStr = idStr || 'toast';
            if (idStr === 'toast') {
                document.getElementById('toast_wrap').style.visibility = 'hidden';
            } else {
                $(idStr).hidden();                
            }
        },

        randNum: function(minnum , maxnum){
            return Math.round(minnum + Math.random() * (maxnum - minnum));
        },

        setPreviousFocus: function(selector) {
            Cookie.set('previous_focus', selector, 1);
        },

        getPreviousFocus: function() {
            return Cookie.get('previous_focus');
        },

        setAction: function(action) {
            Cookie.set('action', action, 1);
        },

        getAction: function() {
            return Cookie.get('action');
        },

        setNav: function(selector) {
            Cookie.set('nav', selector, 1);
        },

        getNav: function() {
            return Cookie.get('nav');
        }
    };

    var Dialog = {
        create: function(argument) {
            var domId = argument.domId || "",
                message = argument.message || "";

            if ($(domId)) {
                if (message && $(domId + "_message")) {
                    $(domId + "_message").obj.innerHTML = message;
                }
                $("dialog").obj.innerHTML = $(domId).obj.outerHTML;
            }

            $("dialog").show();
            return this;
        },
        isShow: function() {
            return !$("dialog").isHidden();
        },
        destroy: function() {
            $("dialog").hidden();
        }
    };

    var Flicker = {
        start: function (dom_select) {
            this.timer = setInterval(function () {
                if(dom_select.isHidden()) {
                    dom_select.show();
                } else {
                    dom_select.hidden();
                }
            }, 500);
        },
        stop: function () {
            if(typeof this.timer !== "undefined") {
                clearInterval(this.timer);
            }
        }
    };

    // var Scroll = {
    //     start: function (id) {
    //         this.scrollId = id;
    //         this.innerHtml = id.obj.innerHTML;
    //         if (this.getBt(this.innerHtml) > 20) {
    //             id.obj.innerHTML = '<marquee behavior="alternate" direction="left" scrollamount="1">' + this.innerHtml + '</marquee>';
    //         }
    //     },
    //     stop: function () {
    //         if (this.scrollId) {
    //             this.scrollId.obj.innerHTML = this.innerHtml;
    //             this.scrollId = undefined;
    //         }
    //     },
    //     getBt: function(str){
    //         var char = str.replace(/[^\x00-\xff]/g, '**');
    //         return char.length;
    //     }
    // };
    
    var Scroll = {
        start: function (dom) {
            if (!dom) return;
            this.innerHtml = dom.obj.innerHTML;
            if (this.innerHtml.indexOf('</marquee>') > 0) return;
            if (this.getBt(this.innerHtml) > 20) {
                dom.obj.innerHTML = '<marquee behavior="alternate" direction="left" scrollamount="1">' + this.innerHtml + '</marquee>';
            }
        },
        stop: function (dom) {
            if (!dom) return;
            var innerHtml = dom.obj.innerHTML;
            if (innerHtml.indexOf('</marquee>') > 0)  {
                innerHtml = innerHtml.replace(/<marquee.*>(.*)<\/marquee>/, '$1');
                dom.obj.innerHTML = innerHtml;
            }
        },
        getBt: function(str){
            var char = str.replace(/[^\x00-\xff]/g, '**');
            return char.length;
        }
    };

    var Nevigate = function(argument) {
        return new Nevigate.fn.init(argument);
    };

    Nevigate.fn = Nevigate.prototype = {
        constructor: Nevigate,
        initialize: function(dom_id) {
            this.current_button = this.get(dom_id);
            this.current_dom = this.current_button["current_dom"];
            this.dom_wrap = this.current_button["dom_wrap"];
            this.dom_focus = this.current_button["dom_focus"];
            this.dom_focus_img = this.current_button["dom_focus_img"];
            this.domSelect = this.current_button["dom_select"];
            this.current_btn_info = this.current_button["btn_info"];
            this.dom_scroll = this.current_button["dom_scroll"];
            this.dom_flag = this.current_button["dom_flag"];
            var currentId = this.current_dom.obj.id;
            // 设置放大class
            (/list|card|nav/.test(currentId)) && (this.current_dom.obj.className = "scale");

            if (this.dom_focus) {
                if (this.current_btn_info && this.current_btn_info["focus_image"]) {
                    this.dom_focus_img.src = this.current_btn_info["focus_image"];
                }
                this.dom_focus.show();
                this.dom_wrap.hidden();
            }

            if (this.domSelect) {
                this.domSelect.show();
                (/list|card|nav/.test(currentId)) && (this.domSelect.obj.className = "scale");
                if (Utils.inArray(this.domSelect.obj.className.split(' '), 'flicker') !== -1) {
                    Flicker.start(this.domSelect);
                }
            }

            if (this.dom_scroll) {
                Scroll.start(this.dom_scroll);
            }

            if(this.dom_flag){
                this.dom_flag.obj.className = "scale";
            }

            Utils.call(this.current_button["onfocus"], [this.domSelect, this.current_dom]);
        },
        get: function(id) {
            if($(id)) {
                return this.elementStore[id];
            }
        },
        //获取所有需要设置焦点的元素坐标
        getCoordinate: function() {
            var data = {};
            var doms = document.getElementsByTagName('img');
            for(var i = doms.length - 1; i >= 0; i--) {
                domId = doms[i].id;
                if (domId && (domId.indexOf('page_') === 0 || domId.indexOf('focus_') === 0 || domId.indexOf('back_') === 0)) {
                    var pLeft = this.getElementLeft(domId);
                    var pTop = this.getElementTop(domId);
                    var ele = $(domId).obj;
                    var width = ele.width;
                    var height = ele.height;
                    var xHalf = ele.width * 0.5;
                    var yHalf = ele.height * 0.5;
                    data[domId] = {
                        'left': {'x': pLeft, 'y': pTop + yHalf},
                        'top': {'x': pLeft + xHalf, 'y': pTop},
                        'right': {'x': pLeft + width, 'y': pTop + yHalf},
                        'bottom': {'x': pLeft + xHalf, 'y': pTop + height},
                        'top_left': {'x': pLeft, 'y': pTop},
                        'top_right': {'x': pLeft + width, 'y': pTop},
                        'bottom_left': {'x': pLeft, 'y': pTop + height},
                        'bottom_right': {'x': pLeft + width, 'y': pTop + height}
                    };
                    this.arrayIds.push(domId);
                }
            }
            return data;
        },
        getElementLeft: function(ele) {
            var element = $(ele).obj;
            var actualLeft = element.offsetLeft;
            var current = element.offsetParent;
            while (current !== null) {
                actualLeft += current.offsetLeft;
                current = current.offsetParent;
            }
            return actualLeft;
        },
        getElementTop: function(ele) {
            var element = $(ele).obj;
            var actualTop = element.offsetTop;
            var current = element.offsetParent;
            while (current !== null) {
                actualTop += current.offsetTop;
                current = current.offsetParent;
            }
            return actualTop;
        },
        getDistance: function(point, start, end) {
            var vertical = (start.x === end.x);
            if (vertical) {
                if (point.y < start.y) {
                    return Math.sqrt((point.x - start.x) * (point.x - start.x) + (point.y - start.y) * (point.y - start.y));
                } else if (point.y >= start.y && point.y <= end.y) {
                    return Math.abs(start.x - point.x);
                } else {
                    return Math.sqrt((point.x - end.x) * (point.x - end.x) + (point.y - end.y) * (point.y - end.y));
                }
            } else {
                if (point.x < start.x) {
                    return Math.sqrt((point.x - start.x) * (point.x - start.x) + (point.y - start.y) * (point.y - start.y));
                } else if (point.x >= start.x && point.x <= end.x) {
                    return Math.abs(start.y - point.y);
                } else {
                    return Math.sqrt((point.x - end.x) * (point.x - end.x) + (point.y - end.y) * (point.y - end.y));
                }
            }
        },
        getLeftDom: function(element) {
            var key, data = this.arr_data, dom_id = null, d = 0, distance = 1280;
            for(key in data) {
                //如果遍历的元素左坐标在当前元素右坐标的坐标系的一二象限，直接返回。
                if(data[key].right.x > data[element].left.x) continue;
                d = this.getDistance(data[element].left, data[key].top_right, data[key].bottom_right);
                distance > d && ( distance = d, dom_id = key);
            }
            return dom_id;
        },
        getRightDom: function(element) {
            var key, data = this.arr_data, dom_id = null, d = 0, distance = 1280;
            for(key in data) {
                //如果遍历的元素右坐标在当前元素左坐标的坐标系的三四象限，直接返回。
                if(data[key].left.x < data[element].right.x) continue;
                d = this.getDistance(data[element].right, data[key].top_left, data[key].bottom_left);
                distance > d && ( distance = d, dom_id = key);
            }
            return dom_id;
        },
        getUpDom: function(element) {
            var key, data = this.arr_data, dom_id = null, d = 0, distance = 720;
            for(key in data) {
                //如果遍历的元素底部坐标在当前元素顶部坐标的坐标系的一四象限，直接返回。
                if(data[key].bottom.y > data[element].top.y) continue;
                d = this.getDistance(data[element].top, data[key].bottom_left, data[key].bottom_right);
                distance > d && ( distance = d, dom_id = key);
            }
            return dom_id;
        },
        getDownDom: function(element) {
            var key, data = this.arr_data, dom_id = null, d = 0, distance = 720;
            for(key in data) {
                //如果遍历的元素顶部坐标在当前元素底部坐标的坐标系的二三象限，直接返回。
                if(data[key].top.y < data[element].bottom.y) continue;
                d = this.getDistance(data[element].bottom, data[key].top_left, data[key].top_right);
                distance > d && ( distance = d, dom_id = key);
            }
            return dom_id;
        },
        enter: function(evt) {
            Utils.setAction("enter");
            if (this.current_button["action"]) {
                Utils.call(this.current_button["action"]);
            } else if(this.current_dom.title) {
                (/list|card/.test(this.current_dom.obj.id)) && Utils.setPreviousFocus(this.current_dom.obj.id);
                window.location.href = $(this.current_dom.obj.id).title;
            }
        },

        back: function(evt) {
            var url = $("global_back").url;
            if (Utils.isEmpty(url)) return;
            Utils.setAction("back");
            window.location.href = url;
        },

        configElements: function() {
            var buttons = {};
            var ids = this.arrayIds;
            if (this.routeType) {
                buttons = this.routes;
            }
            for(var i = ids.length - 1; i >= 0; i--) {
                var dom_id = ids[i];
                if (!this.routeType) {
                    buttons[dom_id] = {
                        "left": this.getLeftDom(dom_id),
                        "right": this.getRightDom(dom_id),
                        "up": this.getUpDom(dom_id),
                        "down": this.getDownDom(dom_id)
                    };
                    if (this.routes && this.routes[dom_id]) {
                        var route = this.routes[dom_id];
                        for (var key in route) {
                            if (Utils.inArray(["left", "right", "up", "down"], key) !== -1) {
                                if ($(route[key]) || route[key] == null) {
                                    buttons[dom_id][key] = route[key];
                                }
                            } else {
                                buttons[dom_id][key] = route[key];
                            }
                        }
                    }
                }

                if (this.btn_info && this.btn_info[dom_id]) {
                    buttons[dom_id]["btn_info"] = this.btn_info[dom_id];
                }

                if (buttons[dom_id]) {
                    buttons[dom_id]["current_dom"] = $(dom_id);
                    buttons[dom_id]["dom_wrap"] = $("div_"+dom_id);
                    buttons[dom_id]["dom_focus"] = $(dom_id+"_focus");
                    buttons[dom_id]["dom_focus_img"] = $("img_"+dom_id+"_focus");
                    buttons[dom_id]["dom_select"] = $(dom_id + "_select");
                    buttons[dom_id]["dom_scroll"] = $(dom_id+"_scroll");
                    buttons[dom_id]["dom_flag"] = $(dom_id+"_flag");
                }
            }
            //debug模式下打印导航路由信息，全量路由配置时复制此处打印数据
            //全量路由配置时，js不再计算坐标，效率会提高。
            if (debug) {
                var logs = {};
                for (var key in buttons) {
                    logs[key] = {};
                    logs[key]['left'] = buttons[key].left;
                    logs[key]['right'] = buttons[key].right;
                    logs[key]['up'] = buttons[key].up;
                    logs[key]['down'] = buttons[key].down;
                }
                log(JSON.stringify(logs));
            }
            return buttons;
        },
        move: function(action) {
            var currentId = this.current_dom.obj.id;
            ret = Utils.call(
                this.current_button["onmove"],
                [this.current_button, action]
            );

            Utils.call(
                this.current_button["move_" + action],
                [this.current_button, action]
            );

            if (ret) {
                return false;
            }

            var next_dom = this.current_button[action];

            if(!$(next_dom)) {
                return;
            }

            (/list|card|nav/.test(currentId)) && (this.current_dom.obj.className = "");


            if (this.dom_focus) {
                this.dom_focus.hidden();
                this.dom_wrap.show();
            }

            if (this.domSelect) {
                (/list|card|nav/.test(currentId)) && (this.domSelect.obj.className = "");
                this.domSelect.hidden();
            }

            if(this.dom_flag){
                this.dom_flag.obj.className = "";
            }

            Utils.call(
                this.current_button["onblur"],
                [this.current_button, next_dom]
            );

            Scroll.stop(this.current_button['dom_scroll']);

            Flicker.stop();

            this.initialize(next_dom);
        }
    };

    Nevigate.fn.init = function(arg) {
        if (debug) {
            this.start = new Date().getTime();
        }
        this.arrayIds = [];
        this.arr_data = this.getCoordinate();
        this.focus = arg.focus || "";
        this.routeType = arg.routeType || false;
        this.routes = arg.routes || {};
        this.eventKey = arg.eventKey || {};
        this.btn_info = arg.info || {};
        this.elementStore = this.configElements();
        this.prev_dom = Utils.getPreviousFocus();
        this.prev_action = Utils.getAction();

        if (this.prev_action === "back" && $(this.prev_dom)) {
            this.initialize(this.prev_dom);
        } else {
        	if (this.get(this.focus)) {
	            this.initialize(this.focus);
	        } else if (this.arrayIds[this.arrayIds.length - 1]) {
	            this.initialize(this.arrayIds[this.arrayIds.length - 1]);
	        }
        }

        document.onkeyup = keyUpEvent;
        document.onkeydown = keyDownEvent;

        var self = this;

        evtMap = {
            "left": function(evt) {
                self.move("left");
            },
            "right": function(evt) {
                self.move("right");
            },
            "up": function(evt) {
                self.move("up");
            },
            "down": function(evt) {
                self.move("down");
            },
            "enter": function(evt) {
                self.enter();
            },
            "back": function(evt) {
                evt.preventDefault();
                self.back();
            }
        };

        if (this.eventKey) {
            for (var i in this.eventKey) {
                evtMap[i] = this.eventKey[i];
            }
        }

        if (debug) {
            this.end = new Date().getTime();
            log('Execution time：' + (this.end - this.start) + 'ms');
        }
    };

    var Page = function() {
        var self = this;
        self.filter = {};
        self.pages_info = {};
    };

    Page.prototype = {
        set_filter: function(key, value) {
            if(typeof(value) === "object") {
                for(var k in value){
                    this.filter[k] = value[k];
                }
            } else {
                this.filter[key] = value;
            }
        },
        add_page_info: function(page_key, dict_data) {
            this.pages_info[page_key] = dict_data;
        },
        get_page_info: function(page_key) {
            if(this.pages_info[page_key]) {
                return this.pages_info[page_key];
            }
            return null;
        },
        refresh: function(page_name) {
            var ret = {};
            var filter = this.filter;
            var pages_info  = this.pages_info;
            for(var key in pages_info) {
                var p = pages_info[key];
                var prev_page_id = p["prev_page_id"];
                var next_page_id = p["next_page_id"];
                var current_page = p["current_page"];
                var number_of_page = p["number_of_page"];
                ret[key] = current_page;
            }
            for(var fk in filter) {
                ret[fk] = filter[fk];
            }
            if (prev_page_id && page_name === "prev_page") {
                if (current_page === 1) {
                    ret["focus"] = next_page_id;
                } else {
                    ret["focus"] = prev_page_id;
                }
            } else if (next_page_id && page_name === "next_page") {
                if (current_page === number_of_page) {
                    ret["focus"] = prev_page_id;
                } else {
                    ret["focus"] = next_page_id;
                }
            }
            var url = window.location.href.split("?")[0];
            var params =[];
            for(var k in ret) {
                params.push(k+"="+ret[k]);
            }
            url = url + "?" + params.join("&");
            window.location.href =  url;
        },
        prev_page: function(page_key) {
            if (!arguments[0]) {
                page_key = "p";
            }
            var page_info = this.get_page_info(page_key);
            if(page_info.current_page === 1) {
                return;
            }
            page_info.current_page = page_info.current_page - 1;
            this.refresh("prev_page");
        },
        next_page: function(page_key) {
            if (!arguments[0]) {
                page_key = "p";
            }
            var page_info = this.get_page_info(page_key);
            if(page_info.current_page === page_info.number_of_page) {
                return;
            }
            page_info.current_page = page_info.current_page + 1;
            this.refresh("next_page");
        }
    };

    var Cycle = function() {
        this.init.apply(this, arguments);
    };

    Cycle.prototype = {
        init: function (columns, nevigate, switch_fun, begin, end, max_index, first_cols) {
            this.columns = columns;
            this.nevigate = nevigate;
            this.begin = parseInt(begin) || 0;
            this.end = parseInt(end) || 2;
            this.max_index = max_index || 2;
            this.first_cols = first_cols || 1;
            this.len = this.columns.length;
            this.switch_fun = switch_fun;
            this.showCursor();
        },
        switched: function (dir) {
            if(dir === "down") {
                if(this.end < this.len - 1) {
                    ++this.begin;
                    ++this.end;
                }
            } else if(dir === "up") {
                if(this.begin > 0) {
                    --this.begin;
                    --this.end;
                }
            }

            for (var i = this.begin, j = this.first_cols; i <= this.end; ++i, ++j) {
                this.switch_fun(this.columns, i, j);
            }

            this.showCursor();
        },
        move: function (current_button, dir) {
            var index = current_button["index"];
            Scroll.stop(current_button['dom_scroll']);

            if(index === this.max_index && dir === "down") {
                this.switched("down");
            } else if(index === 0 && dir === "up") {
                this.switched("up");
            }
        },
        showCursor: function () {
            this.end < this.len - 1 ? $("cursor_page_next").show() : $("cursor_page_next").hidden();
            this.begin > 0 ? $("cursor_page_prev").show() : $("cursor_page_prev").hidden();
        }
    };

    Nevigate.fn.init.prototype = Nevigate.prototype;

    window.Nevigate = Nevigate;

    window.Page = Page;

    window.Utils = Utils;

    window.Cycle = Cycle;

    window.Dialog = Dialog;

    window.Cookie = Cookie;

    window.Scroll = Scroll;

    window.log = log;

    window.ajax = ajax;

    window.lazyload = lazyload;

    win.$ = win.u = query;

    document.onkeyup = keyUpEvent;
	document.onkeydown = keyDownEvent;
	module.export = { Nevigate, Page, Utils, Cycle, Dialog, Cookie, Scroll, log, ajax, lazyload };

})(window);
