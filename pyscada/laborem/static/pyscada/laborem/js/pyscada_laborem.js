/* Javascript library for the PyScada-LaboREM web client based on jquery,

version 0.7.2

Copyright (c) 2018 Camille Lavayssière
Licensed under the GPL.

*/


$('button.write-task-form-top10-set').click(function(){
    name_form = $(this.form).attr('name');
    tabinputs = document.forms[name_form].getElementsByTagName("input");
    ok_button = document.forms[name_form].getElementsByTagName("button");
    ok_button[0].disabled = true;
    ok_button[0].innerHTML = "Réponse envoyée !"
    mb_id = $('.list-dut-item.active').data('motherboard-id');
    request_data = {}
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
        if (~data_plug_name.indexOf('ROBOT')) {
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
        if (robot ==='1') {$(".btn-next").attr("href", '#robot'); $(".btn-next").show();}
        else if (robot ==='0') {$(".btn-next").attr("href", '#preconf'); $(".btn-next").show();}
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
        if (robot ==='1') {$(".btn-previous").attr("href", '#robot'); $(".btn-previous").show();}
        else if (robot ==='0') {$(".btn-previous").attr("href", '#preconf'); $(".btn-previous").show();}
        else {$(".btn-previous").hide();}
        if (expe !='') {$(".btn-next").attr("href", '#' + expe); $(".btn-next").show();}
        else {$(".btn-next").hide();}
    }else if (actual_hash === "bode") {
        $(".btn-previous").attr("href", '#expe_choice');
        $(".btn-previous").show();
        $(".btn-next").hide();
    }else if (actual_hash === "spectrum") {
        $(".btn-previous").attr("href", '#expe_choice');
        $(".btn-previous").show();
        $(".btn-next").hide();
    }else if (actual_hash === "viewer") {
        $(".btn-previous").hide();
        $(".btn-next").hide();
    }
};

function reset_page(page_name) {
    if (page_name === "start") {
        reset_robot_bases();
        reset_selected_plug()
        reset_selected_expe()
    }else if (page_name === "plugs") {
        reset_robot_bases();
        reset_selected_plug()
        reset_selected_expe()
    }else if (page_name === "preconf") {
        reset_robot_bases();
        reset_selected_expe()
    }else if (page_name === "robot") {
        reset_robot_bases();
        reset_selected_expe()
    }else if (page_name === "expe_choice") {
        reset_selected_expe()
        move_robot("move");
    }else if (page_name === "bode") {
    }else if (page_name === "spectrum") {
    }else if (page_name === "viewer") {
    }
};

function move_robot(mov) {
    $.ajax({
        type: 'post',
        url: ROOT_URL+'form/move_robot/',
        data: {move:mov},
        success: function (data) {

        },
        error: function(data) {
            add_notification('move robot failed',3);
        }
    });
};

function reset_selected_plug() {
    $('.list-dut-item.active').removeClass('active');
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
    $('.dropdown-base').removeClass('active');
    $('.dropdown-base').show();
    $('.ui-dropdown-robot-bnt').each(function() {
        $(this)[0].innerHTML = "------- ";
    })
    $.ajax({
        type: 'post',
        url: ROOT_URL+'form/reset_robot_bases/',
        data: {},
        success: function (data) {
        },
        error: function(data) {
            add_notification('reset robot bases failed',3);
        }
    });
    move_robot("drop");
};

function change_plug_img($this, $img) {
    $(".img-plug").attr("src",$img);
};

function change_plug_selected_motherboard(mb_id, plug_id, plug_name) {
    if (mb_id === "" || plug_id === ""){
        add_notification('mb_id or plug_id empty',3);
    }else{
        $.ajax({
            type: 'post',
            url: ROOT_URL+'form/write_plug/',
            data: {mb_id:mb_id, plug_id:plug_id},
            success: function (data) {
                $(".btn-next").show();
            },
            error: function(data) {
                add_notification('write plug selected failed',3);
            }
        });
    };
};

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
                                    input_group[i].className -= " hidden";
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

function check_users() {
    if(typeof $($('.list-dut-item')[0]).data('motherboard-id') == 'undefined'){mb_id = 0}else{mb_id = $($('.list-dut-item')[0]).data('motherboard-id')};
    $.ajax({
        type: 'post',
        url: ROOT_URL+'form/check_users/',
        data: {mb_id:mb_id},
        success: function (data) {
            $(".waitingusers-item").remove();
            $(".table-waitingusers tbody").append(data['waitingusers']);
            $(".activeuser-item").remove();
            $(".table-activeuser tbody").append(data['activeuser']);
            if (data['user_type'] == 1 && window.location.hash.substr(1) != "viewer") {
                window.location.href = "#viewer";
            }else if (data['user_type'] == 2 && window.location.hash.substr(1) == "viewer") {
                window.location.href = "#start";
            }
            if (data['user_type'] == 1) {
                $(".dropdown-WaitingList-toggle")[0].innerHTML = ' Waiting : ';
                $(".dropdown-WaitingList-toggle").append(data['titletime']);
                $(".dropdown-WaitingList-toggle").append(' <strong class="caret"></strong>');
                $(".dropdown-WaitingList-toggle").prepend('<span class="glyphicon glyphicon-time"></span>');
            }else if (data['user_type'] == 2) {
                $(".dropdown-WaitingList-toggle")[0].innerHTML = ' Working : ';
                $(".dropdown-WaitingList-toggle").append(data['titletime']);
                $(".dropdown-WaitingList-toggle").append(' <strong class="caret"></strong>');
                $(".dropdown-WaitingList-toggle").prepend('<span class="glyphicon glyphicon-time"></span>');
            }else if (data['user_type'] == 0) {
                $(".dropdown-WaitingList-toggle")[0].innerHTML = ' Waiting List ';
                $(".dropdown-WaitingList-toggle").append(' <strong class="caret"></strong>');
                $(".dropdown-WaitingList-toggle").prepend('<span class="glyphicon glyphicon-time"></span>');
            }
            if (data['timeline_start'] != DATA_FROM_TIMESTAMP) {
                DATA={}
                DATA_FROM_TIMESTAMP = data['timeline_start']
                DATA_DISPLAY_FROM_TIMESTAMP = data['timeline_start']
            }
            if (typeof data['message_laborem'] != 'undefined' && data['message_laborem'] != '') {
                $(".message-laborem h2")[0].innerHTML = ' ' + data['message_laborem'];
                $(".message-laborem h2").prepend('<img id="laborem-loadingAnimation" style="height:30px;padding-bottom:3px;" src="/static/pyscada/img/load.gif" alt="loading">');
                $(".message-laborem").stop().CSSAnimate({"top":51},500);
            }else {
                $(".message-laborem h2")[0].innerHTML = '';
                oh = $(".message-laborem").outerHeight(true);
                $(".message-laborem").stop().CSSAnimate({"top":-(oh - 51)},500);
            }
            if (typeof data['progress_bar'] != 'undefined' && data['progress_bar'] != '') {
                $($(".progress-bar")[0]).css('width', data['progress_bar'] + '%');
                $(".progress-bar")[0].innerHTML = data['progress_bar'] + '%';
                $($(".progress-bar")[0]).removeClass("hidden");
            }else {
                $(".progress-bar")[0].className -= " hidden";
                $(".progress-bar")[0].className += " hidden";
            }
            if (typeof data['summary'] != 'undefined' && data['summary'] != '') {
                $(".summary ul")[0].innerHTML = data['summary']
                $($(".summary")[0]).removeClass("hidden");
            }else {
                $(".summary")[0].className -= " hidden";
                $(".summary")[0].className += " hidden";
            }
        },
        error: function(data) {
            add_notification('write plug selected failed',3);
        }
    });
}

$( document ).ready(function() {
    //change text and link of PyScada in navbar
    $(".navbar-brand").attr("href", "");
    $(".navbar-brand").removeAttr("target");
    $(".navbar-brand")[0].innerHTML = ' PyScada-LaboREM';
    $(".navbar-brand").prepend('<span class="glyphicon glyphicon-home"></span>');
    $(".btn-previous").hide();

    //if not starting on #start page redirect to this hash
    if (window.location.hash.substr(1) != "start"){window.location.href = "#start";}

    //Send info and actualize data
    setInterval(function() {check_users()}, 1000);

    //Load next and previous button at start
    query_previous_and_next_btn()

    //load top10 ranking at start
    reload_top10_ranking();

    //reset the pages settings at start
    reset_page(window.location.hash.substr(1));

    $(window).on('hashchange', function() {
        //reset the pages settings to force the user to interact with
        reset_page(window.location.hash.substr(1));

        //refresh previous and next buttom
        query_previous_and_next_btn()

        // Check if we are on a page that need to show the TOP10QAs
        refresh_top10_qa();
    });

    //Change the link of btn next/previous on click
    $('.btn-next, .btn-previous').on('click', function() {
        //query_previous_and_next_btn()
    });

    // actualize the picture of the dut selector for LaboREM with the list selection
    $('.list-dut-item').on('click', function() {
        var $this = $(this);
        var $img = $this.data('img');
        var $mb_id = $this.data('motherboard-id');
        var $plug_id = $this.data('plug-id');
        var $plug_name = $this.data('plug-name');

        $('.list-dut-item.active').removeClass('active');
        $this.toggleClass('active');

        change_plug_img($this, $img)
        change_plug_selected_motherboard($mb_id, $plug_id, $plug_name)
        query_previous_and_next_btn()
    });

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
        change_base_selected_element($($this[0]).parents(".dropdown-robot")[0].id, $this[0].id)
        query_previous_and_next_btn();
        if (base_empty === 'no') {$(".btn-next").show();}
    });

    // Active the selected item in a listbox and disable it in others listboxes
    $('.dropdown-afg-function').on('click', function() {
        var $this = $(this);
        dropdown_item = $("#" + $($this[0]).parents(".sub-page")[0].id + " .dropdown-afg-function")
        for (i=0;i<dropdown_item.length;i++){
            if ($(dropdown_item[i]).parents(".dropdown-afgfunctions")[0].id === $($this[0]).parents(".dropdown-afgfunctions")[0].id) {
                $(dropdown_item[i]).removeClass('active');
            }
        }
        $this.addClass('active');
        $($this[0]).parents(".dropdown-afgfunctions").children(".btn").children(".ui-dropdown-afgfunctions-btn")[0].innerHTML = $($this[0]).children()[0].innerHTML;
        variable_property = $(this).data('name');
        value = $(this).data('value').toString();
        if (value === ""){
            add_notification('please provide a value',3);
        }else {
            $.ajax({
                type: 'post',
                url: ROOT_URL+'form/write_property/',
                data: {variable_property:variable_property, value:value},
                success: function (data) {

                },
                error: function(data) {
                    add_notification('write plug selected failed',3);
                }
            });
        }
    });
});