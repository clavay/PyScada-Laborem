/* Javascript library for the PyScada-Laborem web client based on jquery,

version 0.7.3

Copyright (c) 2018 Camille Lavayssière
Licensed under the GPL.

*/
var version = "0.7.3"
var CONNECTION_ID = ""
var USER_TYPE = ""
var CONNECTION_ACCEPTED = 0
var WAITING_USERS_DATA = {}

function reload_top10_ranking() {
    $.ajax({
        type: 'post',
        url: ROOT_URL+'form/rank_top10/',
        data: {},
        success: function (data) {
            $(".top10-item").remove();
            $(".table-top10 tbody").append( data );
        },
        error: function(data) {
            add_notification('rank top10 failed',3);
            console.log('rank top10 failed');
        }
    });
};

function query_previous_and_next_btn() {
    actual_hash = window.location.hash.substr(1);
    robot = ""
    expe = ""

    // finding if a plug is selected and if have ROBOT in the name
    data_plug_name = $('.list-dut-item.active').attr('data-plug-name');
    if (typeof data_plug_name != 'undefined') {
        if ($('.list-dut-item.active .badge.robot').length) {
            robot = '1';
        }else {
            robot = '0';
        }
    }

    // finding if an expe is selected
    if (typeof $('.expe_list_item.active').attr('name') != 'undefined') {
        expe = $('.expe_list_item.active').attr('name')
    }

    if (actual_hash === "start") {
        $(".btn-previous").hide();
        $(".btn-next").attr("href", '#plugs');
        $(".btn-next").show();
    }else if (actual_hash === "plugs") {
        $(".btn-previous").attr("href", '#start');
        $(".btn-previous").show();
        if (robot ==='1') {
            $(".btn-next").attr("href", '#robot');
            $(".btn-next").show();
        }
        else if (robot ==='0') {
            $(".btn-next").attr("href", '#preconf');
            $(".btn-next").show();
        }
        else {$(".btn-next").hide();}
    }else if (actual_hash === "preconf") {
        $(".btn-previous").attr("href", '#plugs');
        $(".btn-previous").show();
        $(".btn-next").attr("href", '#expe_choice');
        $(".btn-next").show();
    }else if (actual_hash === "robot") {
        $(".btn-previous").attr("href", '#plugs');
        $(".btn-previous").show();
        $(".btn-next").attr("href", '#expe_choice');
        $(".btn-next").hide();
    }else if (actual_hash === "expe_choice") {
        if (robot ==='1') {
            $(".btn-previous").attr("href", '#robot');
            $(".btn-previous").show();
        }
        else if (robot ==='0') {
            $(".btn-previous").attr("href", '#preconf');
            $(".btn-previous").show();
        }
        else {$(".btn-previous").hide();}
        if (expe !='') {
            $(".btn-next").attr("href", '#' + expe);
            $(".btn-next").show();
        }
        else {$(".btn-next").hide();}
    }else if (actual_hash === "bode") {
        $(".btn-previous").attr("href", '#expe_choice');
        $(".btn-previous").show();
        $(".btn-next").hide();
    }else if (actual_hash === "spectrum") {
        $(".btn-previous").attr("href", '#expe_choice');
        $(".btn-previous").show();
        $(".btn-next").hide();
    }else if (actual_hash === "viewer" || actual_hash === "waiting" || actual_hash === "disconnect" || actual_hash === "loading") {
        $(".btn-previous").hide();
        $(".btn-next").hide();
    }
};

function redirect_to_page(page_name) {
    if (CONNECTION_ACCEPTED == -1) {
        window.location.href = "#disconnect";
        return 1;
    }
    if (page_name === "preconf") {
        if ($('.list-dut-item.active .badge.robot').length || !$('.list-dut-item.active').length) { window.location.href = "#plugs";}
    }else if (page_name === "robot") {
        if (!$('.list-dut-item.active .badge.robot').length || !$('.list-dut-item.active').length) { window.location.href = "#plugs";}
    }else if (page_name === "expe_choice") {
        if (!$('.list-dut-item.active').length) {
            window.location.href = "#plugs";
            return 1;
        }else {
            if ($('.list-dut-item.active .badge.robot').length) {
                // Finding if all robot bases are selected
                base_empty = 'no'
                $('.sub-page#robot .ui-dropdown-robot-bnt').each(function() {
                    if ($(this)[0].innerHTML === "------- ") {
                        base_empty = 'yes'
                    }
                })
                if (base_empty === 'yes') {
                    window.location.href = "#robot";
                    return 1;
                }
            }
        }
    }else if (page_name === "bode" || page_name === "spectrum") {
        if (!$('.list-dut-item.active').length) {
            window.location.href = "#plugs";
            return 1;
        }else {
            if ($('.list-dut-item.active .badge.robot').length) {
                // Finding if all robot bases are selected
                base_empty = 'no'
                $('.sub-page#robot .ui-dropdown-robot-bnt').each(function() {
                    if ($(this)[0].innerHTML === "------- ") {
                        base_empty = 'yes'
                    }
                })
                if (base_empty === 'yes') {
                    window.location.href = "#robot";
                    return 1;
                }else {
                    // finding if an expe is selected
                    if (typeof $('.expe_list_item.active').attr('name') == 'undefined') {
                        window.location.href = "#expe_choice";
                        return 1;
                    }else {
                        if (page_name !== $('.expe_list_item.active').attr('name')) {
                            window.location.href = "#" + $('.expe_list_item.active').attr('name');
                            return 1;
                        }
                    }
                }
            }else {
                // finding if an expe is selected
                if (typeof $('.expe_list_item.active').attr('name') == 'undefined') {
                    window.location.href = "#expe_choice";
                    return 1;
                }else {
                    if (page_name !== $('.expe_list_item.active').attr('name')) {
                        window.location.href = "#" + $('.expe_list_item.active').attr('name');
                        return 1;
                    }
                }
            }
        }
    }else if (page_name === "start" || page_name === "plugs") {
        return;
    }else { return;}
}

function reset_page(page_name) {
    if (redirect_to_page(page_name)) { return;};
    if (page_name === "start") {
        $(".camera").show()
        $(".dropdown-WaitingList").show()
        $(".summary.side-menu").show()
        $(".user_stop_btn").hide()
        $('#ViewerModal').modal('hide');
        reset_robot_bases();
        reset_selected_plug();
        reset_selected_expe();
        $("#tooltip").hide();
    }else if (page_name === "plugs") {
        $(".user_stop_btn").hide()
        reset_robot_bases();
        reset_selected_plug();
        reset_selected_expe();
        $("#tooltip").hide();
    }else if (page_name === "preconf") {
        $(".user_stop_btn").hide()
        change_plug_selected_motherboard();
        reset_robot_bases();
        reset_selected_expe();
        $("#tooltip").hide();
    }else if (page_name === "robot") {
        $(".user_stop_btn").hide()
        change_plug_selected_motherboard();
        reset_robot_bases();
        reset_selected_expe();
        $("#tooltip").hide();
    }else if (page_name === "expe_choice") {
        $(".user_stop_btn").hide()
        change_bases();
        change_plug_selected_motherboard();
        update_plots(true);
        reset_selected_expe();
        move_robot("put");
        $("#tooltip").hide();
    }else if (page_name === "bode") {
        $(".user_stop_btn").show()
        $(".user_stop_btn").removeClass("disabled")
        $(".user_stop_btn").html("Arrêter")
        update_plots(false);
        change_bases();
        move_robot("put");
    }else if (page_name === "spectrum") {
        $(".user_stop_btn").show()
        $(".user_stop_btn").removeClass("disabled")
        $(".user_stop_btn").html("Arrêter")
        update_plots(false);
        change_bases();
        move_robot("put");
    }else if (page_name === "viewer") {
        $(".dropdown-WaitingList").show()
        $(".summary.side-menu").show()
        $(".camera").show()
        $(".user_stop_btn").hide()
        update_plots(false);
        $('#ViewerModal').modal('show');
    }else if (page_name === "waiting") {
        $(".dropdown-WaitingList").show()
        $(".summary.side-menu").hide()
        $('#ViewerModal').modal('hide');
        $(".user_stop_btn").hide()
        $(".camera").hide()
    }else if (page_name === "disconnect" || page_name === "loading" ) {
        $('#ViewerModal').modal('hide');
        $(".camera").hide()
        $(".user_stop_btn").hide()
        $(".dropdown-WaitingList").hide()
        $(".summary.side-menu").hide()
    }
};

function update_plots(force) {
    $.each(PyScadaPlots,function(plot_id){
        PyScadaPlots[plot_id].update(force);
    });
}

function move_robot(mov) {
    $.ajax({
        type: 'post',
        url: ROOT_URL+'form/move_robot/',
        data: {move:mov},
        success: function (data) {
            if (typeof data['message_laborem'] != 'undefined' && data['message_laborem'] != '' && window.location.hash.substr(1) != "waiting") {
                $(".message-laborem h2")[0].innerHTML = ' ' + data['message_laborem'];
                $(".user_stop_btn").hide()
                $('#MessageModal').modal('show');
            }else {
                $('#MessageModal').modal('hide');
                $(".user_stop_btn").removeClass("disabled")
                $(".user_stop_btn").html("Arrêter")
                $(".message-laborem h2")[0].innerHTML = '';
            }
        },
        error: function(data) {
            add_notification('move robot failed',3);
        }
    });
};

function reset_selected_plug() {
    $('.list-dut-item.active').removeClass('active');
    $(".img-plug").attr("src",$(".img-plug").data("img"));
    if(typeof $('.list-dut-item').data('motherboard-id') == 'undefined'){mb_id = 0}else{mb_id = $('.list-dut-item').data('motherboard-id')};
    $.ajax({
        type: 'post',
        url: ROOT_URL+'form/reset_selected_plug/',
        data: {mb_id:mb_id},
        success: function (data) {
        },
        error: function(data) {
            add_notification('reset selected plug failed',3);
        }
    });
};

function reset_selected_expe() {
    $('.expe_list_item.active').removeClass('active');
    $.ajax({
        type: 'post',
        url: ROOT_URL+'form/write_property/',
        data: {variable_property:"EXPERIENCE",value:""},
        success: function (data) {

        },
        error: function(data) {
            add_notification('write expe failed',3);
        }
    });
};

function reset_robot_bases() {
    move_robot("drop");
    $('.dropdown-base').removeClass('active');
    $('.dropdown-base').show();
    $('.ui-dropdown-robot-bnt').each(function() {
        $(this)[0].innerHTML = "------- ";
    })
};

function change_plug_selected_motherboard() {
    plug_active = $(".sub-page#plugs .list-dut-item.active");
    mb_id = plug_active.data('motherboard-id');
    plug_id = plug_active.data('plug-id');
    if (mb_id === "" || plug_id === ""){
        add_notification('mb_id or plug_id empty',3);
    }else{
        $.ajax({
            type: 'post',
            url: ROOT_URL+'form/write_plug/',
            data: {mb_id:mb_id, plug_id:plug_id},
            success: function (data) {

            },
            error: function(data) {
                add_notification('write plug selected failed',3);
            }
        });
    };
};

function change_bases() {
    dropdown_item_active = $(".sub-page#robot .dropdown-base.active");
    for (i=0;i<dropdown_item_active.length;i++){
        change_base_selected_element($(dropdown_item_active[i]).parents(".dropdown-robot")[0].id, dropdown_item_active[i].id)
    }
}

function refresh_top10_qa() {
    dropdown_TOP10QA = document.getElementsByClassName("dropdown-TOP10QA");
    pages = document.getElementsByClassName("sub-page");
    for (i=0;i<pages.length;i++){
        if (pages[i].id === window.location.hash.substr(1)) {
            if (pages[i].getElementsByClassName("ShowTOP10QA").length) {
                questions = document.getElementsByClassName("dropdown-TOP10QA")[0].getElementsByClassName("input-group-addon-label");
                input_group = document.getElementsByClassName("dropdown-TOP10QA")[0].getElementsByClassName("input-group");
                form_control = document.getElementsByClassName("dropdown-TOP10QA")[0].getElementsByClassName("form-control");
                ok_button = document.getElementsByClassName("dropdown-TOP10QA")[0].getElementsByClassName("write-task-form-top10-set");
                ok_button[0].disabled = false;
                ok_button[0].innerHTML = "Répondre"
                answers=[]
                mb_id = $('.list-dut-item.active').data('motherboard-id');
                //changes the number and value of the questions
                $.ajax({
                    url: ROOT_URL+'json/query_top10_question/',
                    dataType: "json",
                    type: "POST",
                    data: {mb_id:mb_id, page:pages[i].id},
                    success: function (data) {
                        questions[0].innerHTML = data['question1'];
                        questions[1].innerHTML = data['question2'];
                        questions[2].innerHTML = data['question3'];
                        questions[3].innerHTML = data['question4'];
                        answers[0] = data['answer1'];
                        answers[1] = data['answer2'];
                        answers[2] = data['answer3'];
                        answers[3] = data['answer4'];
                        if ((questions[0].innerHTML != "Question1" && questions[0].innerHTML != "" && questions[0].innerHTML != "undefined")
                        || (questions[1].innerHTML != "Question2" && questions[1].innerHTML != "" && questions[1].innerHTML != "undefined")
                        || (questions[2].innerHTML != "Question3" && questions[2].innerHTML != "" && questions[2].innerHTML != "undefined")
                        || (questions[3].innerHTML != "Question4" && questions[3].innerHTML != "" && questions[3].innerHTML != "undefined")) {
                            $(".dropdown-TOP10QA").removeClass("hidden");
                            $(".dropdown-TOP10QA").show();
                            for (i=0;i<questions.length;i++) {
                                if (questions[i].innerHTML != "Question1" && questions[i].innerHTML != "" && questions[i].innerHTML != "undefined") {
                                    input_group[i].classList.remove("hidden");
                                    if (data['disable']) {
                                        form_control[i].value = answers[i];
                                        form_control[i].disabled = true;
                                        ok_button[0].disabled = true
                                        ok_button[0].innerHTML = "Déjà répondu !"
                                    }else{
                                        form_control[i].disabled = false;
                                        form_control[i].value = "";
                                    }
                                }
                                else {
                                    input_group[i].classList.remove("hidden");
                                    input_group[i].className += " hidden";
                                }
                            }
                        }else {
                            $(".dropdown-TOP10QA").hide();
                        }
                    },
                    error: function(data) {
                        console.log("query top10 question failed");
                        add_notification('query top10 question failed',3);
                    }
                });
            }else {
                $(".dropdown-TOP10QA").hide();
            }
        }
    }
};

function change_base_selected_element(base_id, element_id) {
    if (base_id === "" || element_id === ""){
        add_notification('base_id or element_id empty',3);
    }else{
        $.ajax({
            type: 'post',
            url: ROOT_URL+'form/write_robot_base/',
            data: {base_id:base_id, element_id:element_id},
            success: function (data) {

            },
            error: function(data) {
                add_notification('write plug selected failed',3);
            }
        });
    };
};

function remove_id() {
    if (CONNECTION_ID != "") {
        $.ajax({
            type: 'post',
            url: ROOT_URL+'form/remove_id/',
            data: {connection_id:CONNECTION_ID},
            success: function (data) {
                window.location.href = "#loading";
                check_time();
                check_users();
            },
            error: function(data) {
                console.log('remove_id failed');
            }
        })
    }else {
        check_time();
        remove_id();
    }
}

function check_time() {
    $.ajax({
        type: 'post',
        url: ROOT_URL+'form/check_time/',
        data: {connection_id:CONNECTION_ID},
        success: function (data) {
            if (typeof data['connection_id'] != 'undefined') {CONNECTION_ID = data['connection_id']};
            if (data['connection_accepted'] == "1") {
                CONNECTION_ACCEPTED = 1;
                if (window.location.hash.substr(1) == "disconnect") {
                    window.location.href = "#loading";
                }else if (window.location.hash.substr(1) == "loading") {
                    check_users()
                }
                setTimeout(function() {check_time()}, data['setTimeout']);
            }else {
                CONNECTION_ACCEPTED = -1;
                $('#ViewerModal').modal('hide');
                window.location.href = "#disconnect";
                REFRESH_RATE = 30000;
                //setTimeout(function() {check_time()}, data['setTimeout']);
            }
        },
        error: function(data) {
            console.log('check time failed');
        }
    })
}

function check_users() {
    if(typeof $($('.list-dut-item')[0]).data('motherboard-id') == 'undefined'){mb_id = 0}else{mb_id = $($('.list-dut-item')[0]).data('motherboard-id')};
    $.ajax({
        type: 'post',
        url: ROOT_URL+'form/check_users/',
        data: {mb_id:mb_id},
        success: function (data) {
            data['setTimeout'] = 1000;
            //REFRESH_RATE = 2500;

            // Waiting user part : tbody and title_time
            $(".waitingusers-item").remove();
            if (typeof(data['waiting_users'])==="object"){
                WAITING_USERS_DATA = data['waiting_users'];
                delete data['waiting_users'];
            }else{
                WAITING_USERS_DATA = {}
            }
            title_time = "illimité"
            waiting_users_tbody = ""
            waiting_users_count = 0
            for (var key in WAITING_USERS_DATA) {
                waiting_users_count = Math.max(key, waiting_users_count)
                waiting_users_tbody += '<tr class="waitingusers-item"><td>'
                waiting_users_tbody += WAITING_USERS_DATA[key]['username']
                waiting_users_tbody += '</td><td style="text-align: center">'
                if (data['request_user'] === WAITING_USERS_DATA[key]['username']) {
                    title_time = "";
                    data['viewer_rank'] = key;
                }
                if (WAITING_USERS_DATA[key]['min'] > 0) {
                    if (data['request_user'] === WAITING_USERS_DATA[key]['username']) {
                        title_time += WAITING_USERS_DATA[key]['min'];
                        title_time += ' min '
                    }
                    waiting_users_tbody += WAITING_USERS_DATA[key]['min']
                    waiting_users_tbody += ' min '
                }
                if (data['request_user'] === WAITING_USERS_DATA[key]['username']) {
                    title_time += WAITING_USERS_DATA[key]['sec'];
                    title_time += ' sec'
                    if (WAITING_USERS_DATA[key]['min'] > 0 && WAITING_USERS_DATA[key]['sec'] < 12) {
                        data['viewer_refresh_rate'] = 1;
                    }else {
                        data['viewer_refresh_rate'] = 0;
                    }
                }
                waiting_users_tbody += WAITING_USERS_DATA[key]['sec']
                waiting_users_tbody += ' sec</td></tr>'
            }
            $(".table-waitingusers tbody").append(waiting_users_tbody);

            // Working user part : tbody and title_time
            $(".activeuser-item").remove();
            if (typeof data['active_user'] != 'undefined') {
                active_user_tbody = '<tr class="waitingusers-item"><td>'
                active_user_tbody += data['active_user']['name']
                active_user_tbody += '</td><td style="text-align: center">'
                if (waiting_users_count > 0) {
                    if (data['request_user'] === data['active_user']['name']) {title_time = "";}
                    if (data['active_user']['min'] > 0) {
                        if (data['request_user'] === data['active_user']['name']) {
                            title_time += data['active_user']['min'];
                            title_time += ' min '
                        }
                        active_user_tbody += data['active_user']['min']
                        active_user_tbody += ' min '
                    }
                    if (data['request_user'] === data['active_user']['name']) {
                        title_time += data['active_user']['sec'];
                        title_time += ' sec'
                    }
                    active_user_tbody += data['active_user']['sec']
                    active_user_tbody += ' sec</td></tr>'
                }else {
                    active_user_tbody += title_time
                }
                $(".table-activeuser tbody").append(active_user_tbody);
            }

            // Update wainting list drop down
            if (typeof data['user_type'] != 'undefined') {
                if (data['user_type'] == "viewer") {
                    $(".dropdown-WaitingList-toggle")[0].innerHTML = " Temps d'attente : ";
                    $(".dropdown-WaitingList-toggle").append(title_time);
                    $(".dropdown-WaitingList-toggle").append(' <strong class="caret"></strong>');
                    $(".dropdown-WaitingList-toggle").prepend('<span class="glyphicon glyphicon-time"></span>');
                    if (typeof data['viewer_rank'] != 'undefined' && data['viewer_rank'] < 6) {
                        if (data['viewer_refresh_rate'] == 1) {
                            data['setTimeout'] = 1000;
                            REFRESH_RATE = 1000;
                        }else {
                            data['setTimeout'] = 10000;
                            REFRESH_RATE = 10000;
                        }
                        if (window.location.hash.substr(1) != "viewer" && window.location.hash.substr(1) != "disconnect") {
                            if (CONNECTION_ACCEPTED == 1) {
                                window.location.href = "#viewer";
                            }else if (CONNECTION_ACCEPTED == -1) {
                                window.location.href = "#disconnect";
                            }
                        }
                    }else if (typeof data['viewer_rank'] != 'undefined' && data['viewer_rank'] > 5) {
                        data['setTimeout'] = 30000;
                        REFRESH_RATE = 30000;
                        if (window.location.hash.substr(1) != "waiting" && window.location.hash.substr(1) != "disconnect") {
                            if (CONNECTION_ACCEPTED == 1) {
                                window.location.href = "#waiting";
                            }else if (CONNECTION_ACCEPTED == -1) {
                                window.location.href = "#disconnect";
                            }
                        }
                    }
                }else if (data['user_type'] == "worker") {
                    data['setTimeout'] = 1000;
                    REFRESH_RATE = 1000;
                    $(".dropdown-WaitingList-toggle")[0].innerHTML = ' Actif pour : ';
                    $(".dropdown-WaitingList-toggle").append(title_time);
                    $(".dropdown-WaitingList-toggle").append(' <strong class="caret"></strong>');
                    $(".dropdown-WaitingList-toggle").prepend('<span class="glyphicon glyphicon-time"></span>');
                    if (window.location.hash.substr(1) == "viewer" || window.location.hash.substr(1) == "waiting" || window.location.hash.substr(1) == "loading") {
                        if (CONNECTION_ACCEPTED == 1) {
                            window.location.href = "#start";
                        }else if (CONNECTION_ACCEPTED == -1) {
                            window.location.href = "#disconnect";
                        }
                    }
                }else if (data['user_type'] == "teacher") {
                    data['setTimeout'] = 1000;
                    REFRESH_RATE = 1000;
                    $(".dropdown-WaitingList-toggle")[0].innerHTML = " Liste d'attente ";
                    $(".dropdown-WaitingList-toggle").append(' <strong class="caret"></strong>');
                    $(".dropdown-WaitingList-toggle").prepend('<span class="glyphicon glyphicon-time"></span>');
                }else if (data['user_type'] == "none") {
                    data['setTimeout'] = 1000;
                    REFRESH_RATE = 1000;
                }
            }

            // Timeline part
            if (data['timeline_start'] != DATA_FROM_TIMESTAMP && data['timeline_start'] != '' && typeof data['timeline_start'] != 'undefined') {
                //DATA={}
                //DATA_FROM_TIMESTAMP = data['timeline_start'];
                DATA_DISPLAY_FROM_TIMESTAMP = data['timeline_start'];
                if (data['timeline_stop'] > DATA_FROM_TIMESTAMP && data['timeline_stop'] != '' && typeof data['timeline_stop'] != 'undefined') {
                    //DATA_TO_TIMESTAMP = data['timeline_stop'];
                    DATA_DISPLAY_TO_TIMESTAMP = data['timeline_stop'];
                    DATA_DISPLAY_WINDOW = data['timeline_stop'] - data['timeline_start'];
                }else {
                    //DATA_TO_TIMESTAMP = SERVER_TIME;
                    DATA_DISPLAY_TO_TIMESTAMP = SERVER_TIME;
                    DATA_DISPLAY_WINDOW = DATA_DISPLAY_TO_TIMESTAMP-DATA_DISPLAY_FROM_TIMESTAMP;
                }
            }else {
                //DATA_FROM_TIMESTAMP = SERVER_TIME;
                DATA_DISPLAY_FROM_TIMESTAMP = SERVER_TIME;
                //DATA_TO_TIMESTAMP = SERVER_TIME;
                DATA_DISPLAY_TO_TIMESTAMP = SERVER_TIME;
                DATA_DISPLAY_WINDOW = DATA_DISPLAY_TO_TIMESTAMP-DATA_DISPLAY_FROM_TIMESTAMP;
            }

            //Message Modal part
            if (typeof data['message_laborem'] != 'undefined' && data['message_laborem'] != '' && window.location.hash.substr(1) != "waiting") {
                $(".message-laborem h2")[0].innerHTML = ' ' + data['message_laborem'];
                $('#MessageModal').modal('show');
            }else {
                $('#MessageModal').modal('hide');
                $(".user_stop_btn").removeClass("disabled")
                $(".user_stop_btn").html("Arrêter")
                $(".message-laborem h2")[0].innerHTML = '';
            }

            // Progress bar part
            if (typeof data['progress_bar'] != 'undefined' && data['progress_bar'] != '') {
                $($(".progress-bar")[0]).css('width', data['progress_bar'] + '%');
                $(".progress-bar")[0].innerHTML = data['progress_bar'] + '%';
                $($(".progress-bar")[0]).removeClass("progress-bar-striped active");
            }else {
                $($(".progress-bar")[0]).css('width', '100%');
                $(".progress-bar")[0].innerHTML ='';
                $($(".progress-bar")[0]).removeClass("progress-bar-striped active");
                $(".progress-bar")[0].className += " progress-bar-striped active";
            }

            // Summary part
            summary = '<h3>Résumé</h3>'
            if (typeof data['active_user'] != 'undefined' && typeof data['active_user']['name'] != 'undefined' && data['active_user']['name'] != '') {
                summary += '<li>En train de manipuler : ' + data['active_user']['name'] + '</li>'
            }
            if (typeof data['viewer_rank'] != 'undefined' && data['viewer_rank'] != '') {
                summary += "<li>File d'attente :<ul><li>Rang : " + data['viewer_rank'] + "</li>"
            }
            if (typeof title_time != 'undefined' && title_time != '' && data['user_type'] == 'viewer') {
                summary += "<li>Temps d'attente : " + title_time + '</li></ul></li>'
            }
            if (typeof data['plug']!= 'undefined' && data['plug']!= '') {
                if (typeof data['plug']['name'] != 'undefined' && data['plug']['name'] != '') {
                    summary += "<li>Montage en cours : <ul><li>" + data['plug']['name'] + "</li>"
                }
                if (typeof data['plug']['robot'] != 'undefined' && data['plug']['robot'] != '') {
                    if (data['plug']['robot'] == 'true') {
                        summary += "<li>Modifiable via le robot</li>"
                        for (var base in data['plug']['base']) {
                            summary += "<li>Composant " + base + " : " + data['plug']['base'][base] + "</li>"
                        }
                    summary += "</ul>"
                    }else {
                        summary += "<li>Précablé</li></ul>"
                    }
                }
            }
            if (typeof data['experience'] != 'undefined' && data['experience'] != '') {
                expe_list = $('.expe_list_item')
                for (i=0;i<expe_list.length;i++){
                    if ($(expe_list[i]).attr('name') == data['experience']) {
                        summary += "<li>Expérience en cours : " + expe_list[i].innerHTML + "</li>"
                    }
                }
            }
            if (typeof summary != 'undefined' && summary != '') {
                $(".summary ul").html(summary);
                $(".summary-modal ul").html(summary);
                $(".modal-footer").removeClass("hidden");
                $(".summary").removeClass("hidden");
            }else {
                $(".summary").removeClass("hidden");
                $(".summary").addClass("hidden");
            }
            $($(".camera")[0]).removeClass("hidden");

            //Change text for plug details :
            if (typeof data['plug'] != 'undefined' && typeof data['plug']['name'] != 'undefined' && data['plug']['name'] != '' && typeof data['plug']['description'] != 'undefined' && data['plug']['description'] != '') {
                $(".plug_details.plug_name").html(data['plug']['name'])
                $(".plug_details.plug_description").html(data['plug']['description'])
            }
            if ($('.list-dut-item.active .badge.level').length) {
                $(".plug_details.plug_level").html($('.list-dut-item.active .badge.level')[0].innerHTML)
            }

            // Reload check_users if not on disconnect page (other session active)
            if (window.location.hash.substr(1) != "disconnect") {
                setTimeout(function() {check_users()}, data['setTimeout']);
            }else {
                REFRESH_RATE = 30000;
            }
        },
        error: function(data) {
            console.log('check user failed');
        }
    });
}

function get_experience_list() {
    $.ajax({
        type: 'post',
        url: ROOT_URL+'form/get_experience_list/',
        data: {},
        success: function (data) {
            for (var key in data){
                $(".expe_list").append('<a href="javascript:;" class="list-group-item expe_list_item" name=' + key + '>' + data[key] + '</a>')
            };
            // Change next button and save experience in Variable Property
            $('.expe_list_item').on('click', function() {
                var $this = $(this);
                $('.expe_list_item.active').removeClass('active');
                $this.addClass('active');
                if (typeof $('.expe_list_item.active').attr('name') != 'undefined') {
                    expe = $('.expe_list_item.active').attr('name')
                    $.ajax({
                        type: 'post',
                        url: ROOT_URL+'form/write_property/',
                        data: {variable_property:"EXPERIENCE",value:expe},
                        success: function (data) {

                        },
                        error: function(data) {
                            add_notification('write expe failed',3);
                        }
                    });
                }
                query_previous_and_next_btn();
            });
        },
        error: function(data) {
            console.log('get_experience_list failed');
        }
    })
}

$( document ).ready(function() {
    // Change text and link of PyScada in navbar
    $(".navbar-brand").attr("href", "");
    $(".navbar-brand").removeAttr("target");
    $(".navbar-brand")[0].innerHTML = ' PyScada-Laborem';
    $(".navbar-brand").prepend('<span class="glyphicon glyphicon-home"></span>');
    $(".btn-previous").hide();

    // If not starting on #start page redirect to this hash
    if (window.location.hash.substr(1) != "start"){window.location.href = "#loading";}

    // Send info and actualize data
    setTimeout(function() {check_time()}, 1000);
    setTimeout(function() {check_users()}, 2000);

    // Load next and previous button at start
    query_previous_and_next_btn()

    // Load top10 ranking at start
    reload_top10_ranking();

    // Load experience list at start
    get_experience_list();

    // Reset the pages settings at start
    reset_page(window.location.hash.substr(1));

    $(window).on('hashchange', function() {
        // Reset the pages settings to force the user to interact with
        reset_page(window.location.hash.substr(1));

        // Refresh previous and next buttom
        query_previous_and_next_btn()

        // Check if we are on a page that need to show the TOP10QAs
        refresh_top10_qa();
    });

    // Remove id
    $('.remove_id_btn').on('click', function() {
        remove_id();
    })

    // Stop experience on stop user btn click
    $('.user_stop_btn').on('click', function() {
        $(this).addClass("disabled")
        $(this).html("Patienter...")
        $.ajax({
            type: 'post',
            url: ROOT_URL+'form/write_property/',
            data: {variable_property:"USER_STOP",value:"1"},
            success: function (data) {

            },
            error: function(data) {
                add_notification('write expe failed',3);
            }
        });
    });

    // Actualize the picture of the dut selector for Laborem with the list selection
    $('.list-dut-item').on('click', function() {
        var $this = $(this);
        var $img = $this.data('img');
        //var $mb_id = $this.data('motherboard-id');
        //var $plug_id = $this.data('plug-id');
        //var $plug_name = $this.data('plug-name');

        $('.list-dut-item.active').removeClass('active');
        $this.toggleClass('active');

        $(".img-plug").attr("src",$img);
        //change_plug_selected_motherboard($mb_id, $plug_id, $plug_name)
        query_previous_and_next_btn()
    });

    // For the robot : active the selected item in a listbox and disable it in others listboxes
    $('.dropdown-base').on('click', function() {
        var $this = $(this);
        dropdown_item = $("#" + $($this[0]).parents(".sub-page")[0].id + " .dropdown-base");
        base_empty = 'no'
        for (i=0;i<dropdown_item.length;i++){
            if ($(dropdown_item[i]).parents(".dropdown-robot")[0].id !== $($this[0]).parents(".dropdown-robot")[0].id) {
                if ($(dropdown_item[i])[0].id === $this[0].id) {
                    $(dropdown_item[i]).hide()
                }
                else {
                    $(dropdown_item[i]).show()
                }
                if ($(dropdown_item[i]).parents(".dropdown-robot").children(".btn").children(".ui-dropdown-robot-bnt")[0].innerHTML === "------- ") {
                    base_empty = 'yes'
                }
            }
            else {
                $(dropdown_item[i]).removeClass('active');
            }
        }
        $($this[0]).parents(".dropdown-robot").children(".btn").children(".ui-dropdown-robot-bnt")[0].innerHTML = $($this[0]).children()[0].innerHTML;
        $this.addClass('active');
        //change_base_selected_element($($this[0]).parents(".dropdown-robot")[0].id, $this[0].id)
        query_previous_and_next_btn();
        if (base_empty === 'no') {$(".btn-next").show();}
    });

    // Send answer for TOP10
    $('button.write-task-form-top10-set').click(function(){
        err = false;
        name_form = $(this.form).attr('name');
        id_form = $(this.form).attr('id');
        //tabinputs = document.forms[name_form].getElementsByTagName("input");
        tabinputs = $.merge($('#'+id_form+ ' :text'),$('#'+id_form+ ' :input:hidden'));
        ok_button = $('#'+id_form+ ' :button')
        //ok_button = document.forms[name_form].getElementsByTagName("button");
        mb_id = $('.list-dut-item.active').data('motherboard-id');
        request_data = {}
        for (i=0;i<tabinputs.length;i++){
            value = $(tabinputs[i]).val();
            if (!$(tabinputs[i]).parents(".input-group").hasClass("hidden")) {
                if (value == "" || value == null){
                    $(tabinputs[i]).parents(".input-group").addClass("has-error");
                    $(tabinputs[i]).parents(".input-group").find('.help-block').remove()
                    $(tabinputs[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Please provide a value !</span>');
                    err = true;
                }else {
                    $(tabinputs[i]).parents(".input-group").find('.help-block').remove()
                    $(tabinputs[i]).parents(".input-group").removeClass("has-error")
                }
            }
        }
        if (err) {return;}
        ok_button[0].disabled = true;
        ok_button[0].innerHTML = "Réponse envoyée !"
        for (i=0;i<tabinputs.length;i++){
            tabinputs[i].disabled = true;
            j=i+1;
            value = $(tabinputs[i]).val();
            var_name = $(tabinputs[i]).attr("name");
            $.each($('.variable-config'),function(kkey,val){
                name_var = $(val).data('name');
                if (name_var==var_name){
                    //key = parseInt($(val).data('key'));
                    request_data['value'+j] = value;
                }
            });
        };
        request_data['mb_id'] = mb_id;
        request_data['page'] = window.location.hash.substr(1);
        if (request_data[0] === 'value1:' && request_data[1] === 'value2:' && request_data[2] === 'value3:' && request_data[3] === 'value4:'){
            add_notification('please provide a value',3);
            alert("Please answer something");
        }else{
            $.ajax({
                type: 'post',
                url: ROOT_URL+'form/validate_top10_answers/',
                data:request_data,
                success: function (data) {

                },
                error: function(data) {
                    add_notification('validate_top10_answers error',3);
                    console.log('validate_top10_answers error');
                }
            });
        };
        reload_top10_ranking();
    });
});