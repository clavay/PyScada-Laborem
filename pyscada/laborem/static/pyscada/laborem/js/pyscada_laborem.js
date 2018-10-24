/* Javascript library for the PyScada-LaboREM web client based on jquery,

version 0.7.2

Copyright (c) 2018 Camille Lavayssière
Licensed under the GPL.

*/


$('button.write-task-form-top10-set').click(function(){
    name_form = $(this.form).attr('name');
    tabinputs = document.forms[name_form].getElementsByTagName("input");
    request_data = {}
    for (i=0;i<tabinputs.length;i++){
        j=i+1;
        value = $(tabinputs[i]).val();
        var_name = $(tabinputs[i]).attr("name");
        $.each($('.variable-config'),function(kkey,val){
            name_var = $(val).data('name');
            if (name_var==var_name){
                key = parseInt($(val).data('key'));
                //request_data.push("value" + key + ":" + value);
                request_data['value'+j] = value;
                //item_type = $(val).data('type');
            }
        });
    };
    if (request_data[0] === 'value1:' && request_data[1] === 'value2:' && request_data[2] === 'value3:' && request_data[3] === 'value4:'){
        add_notification('please provide a value',3);
        alert("data empty");
    }else{
        $.ajax({
            type: 'post',
            url: ROOT_URL+'form/validate_top10_answers/',
            data:request_data,
            success: function (data) {

            },
            error: function(data) {
                add_notification('add new write task failed',3);
                alert("Form Set NOK "+data+" - key "+key+" - value "+value+" - item_type "+item_type + " - name "+var_name)
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
        }
    });
};


function query_previous_and_next_btn(actual_hash, direction, robot, expe) {
    $.ajax({
        type: 'post',
        url: ROOT_URL+'json/query_previous_and_next_btn/',
        data: {actual_hash:actual_hash, direction:direction, robot:robot, expe:expe},
        success: function (data) {
            previous = data['previous_page'];
            next = data['next_page'];
            if (previous === "") {
                $(".btn-previous").hide();
            }else if (previous === "=") {
                $(".btn-previous").show();
            }else {
                $(".btn-previous").attr("href", '#' + previous);
                $(".btn-previous").show();
            }
            if (next === "") {
                $(".btn-next").hide();
            }else {
                $(".btn-next").attr("href", '#' + next);
            }
            if (direction === "start") {
                $(".btn-next").show();
            }else {
                //$(".btn-next").hide();
            }
        },
        error: function(data) {
            add_notification('query previous and next btn failed',3);
        }
    });
};

function reset_page(page_name) {
    if (page_name === "robot") {
        $('.dropdown-base').removeClass('active');
        $('.dropdown-base').show();
        $('.ui-dropdown-robot-bnt').text("------- ");
        $(".btn-next").hide();
        move_robot("drop");
    }else if (page_name === "preconf") {
        $(".btn-next").show();
        reset_robot_bases()
        move_robot("drop");
    }else if (page_name === "plugs") {
        $('.list-dut-item').removeClass('active');
        $(".btn-next").hide();
        move_robot("drop");
    }else if (page_name === "start") {
        $(".btn-next").show();
        move_robot("drop");
    }else if (page_name === "bode") {
        $(".btn-next").hide();
    }else if (page_name === "spectrum") {
        $(".btn-next").hide();
    }else if (page_name === "expe_choice") {
        $('.expe_list_item').removeClass('active');
        $(".btn-next").hide();
        move_robot("move");
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

function reset_robot_bases() {
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
                //changes the number and value of the questions
                $.ajax({
                    url: ROOT_URL+'json/query_top10_question/',
                    dataType: "json",
                    type: "POST",
                    data: {},
                    success: function (data) {
                        questions[0].textContent = data['question1'];
                        questions[1].textContent = data['question2'];
                        questions[2].textContent = data['question3'];
                        questions[3].textContent = data['question4'];
                        if ((questions[0].textContent != "Question1" && questions[0].textContent != "")
                        || (questions[1].textContent != "Question2" && questions[1].textContent != "")
                        || (questions[2].textContent != "Question3" && questions[2].textContent != "")
                        || (questions[3].textContent != "Question4" && questions[3].textContent != "")) {
                            $(".dropdown-TOP10QA").removeClass("hidden");
                            $(".dropdown-TOP10QA").show();
                            for (i=0;i<questions.length;i++) {
                                if (questions[i].textContent != "Question1" && questions[i].textContent != "") {
                                    input_group[i].classList.remove("hidden");

                                }
                                else {
                                    input_group[i].className += " hidden"
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

$( document ).ready(function() {
    //change text and link of PyScada in navbar
    $(".navbar-brand").attr("href", "");
    $(".navbar-brand").removeAttr("target");
    $(".navbar-brand").text("PyScada-LaboREM");
    $(".btn-previous").hide();

    //Load next and previous button at start
    query_previous_and_next_btn("start", "start", "", "")

    //Change the link of btn next/previous on click
    $('.btn-next, .btn-previous').on('click', function() {
        var classNames = this.className.split(/\s+/);
        var cls = $.grep(classNames, function(c, i) {
            return $.inArray(c, ['btn-next','btn-previous']) !== -1;
        })[0];
        data_plug_name = $('.list-dut-item.active').attr('data-plug-name');
        actual_hash = window.location.hash.substr(1);
        direction = cls;
        if (typeof data_plug_name != 'undefined') {
            if (~data_plug_name.indexOf('ROBOT')) {
                robot = '1';
            }else {
                robot = '0';
            }
        }else {
            robot = ""
        }
        if (typeof $('.expe_list_item.active').attr('name') != 'undefined') {
            expe = $('.expe_list_item.active').attr('name')
        }else {
            expe = ""
        }
        query_previous_and_next_btn(actual_hash, direction, robot, expe)
    });

    // actualize the picture of the dut selector for LaboREM with the list selection
    $('.list-dut-item').on('click', function() {
        var $this = $(this);
        var $img = $this.data('img');
        var $mb_id = $this.data('motherboard-id');
        var $plug_id = $this.data('plug-id');
        var $plug_name = $this.data('plug-name');

        if (~$plug_name.indexOf('ROBOT')) {
            robot = '1';
        }else {
            robot = '0';
        }
        query_previous_and_next_btn(window.location.hash.substr(1), "idle", robot,"")

        $('.list-dut-item.active').removeClass('active');
        $this.toggleClass('active');

        change_plug_img($this, $img)
        change_plug_selected_motherboard($mb_id, $plug_id, $plug_name)
    });

    $('.expe_list_item').on('click', function() {
        var $this = $(this);
        var expe_name = $this.attr('name');
        robot = ""

        query_previous_and_next_btn(window.location.hash.substr(1), "idle", robot, expe_name);

        $('.expe_list_item.active').removeClass('active');
        $this.addClass('active');
        $(".btn-next").show();
    });

    // For the robot : active the selected item in a listbox and disable it in others listboxes
    $('.dropdown-base').on('click', function() {
        var $this = $(this);
        dropdown_item = document.getElementsByClassName("dropdown-base");
        base_empty = 'no'
        for (i=0;i<dropdown_item.length;i++){
            if ($(dropdown_item[i]).context.parentElement.parentElement.id !== $this.context.parentElement.parentElement.id) {
                if ($(dropdown_item[i]).context.id === $this.context.id) {
                    $(dropdown_item[i]).hide()
                }
                else {
                    $(dropdown_item[i]).show()
                }
                if ($(dropdown_item[i]).context.parentElement.parentElement.innerText.toString() === "------- ") {
                    base_empty = 'yes'
                }
            }
            else {
            $(dropdown_item[i]).removeClass('active');
            }
        }
        if (base_empty === 'no') {$(".btn-next").show();}
        $this.context.parentElement.parentElement.getElementsByClassName('ui-dropdown-robot-bnt')[0].textContent = $this.context.textContent;
        $this.addClass('active');
        change_base_selected_element($this.context.parentElement.parentElement.id, $this.context.id)
    });

    // Active the selected item in a listbox and disable it in others listboxes
    $('.dropdown-afg-function').on('click', function() {
        var $this = $(this);
        //$('.dropdown-afg-function').$('.active').removeClass('active');
        dropdown_item = document.getElementsByClassName("dropdown-afg-function")
        for (i=0;i<dropdown_item.length;i++){
            if ($(dropdown_item[i]).context.parentElement.parentElement.id === $this.context.parentElement.parentElement.id) {
            $(dropdown_item[i]).removeClass('active');
            }
        }
        $this.addClass('active');
        $this.context.parentElement.parentElement.firstElementChild.firstChild.data = $this.context.textContent;
        variable_property_id = $(this).data('key');
        value = $(this).data('value').toString();
        if (value === ""){
            add_notification('please provide a value',3);
        }else {
            $.ajax({
                type: 'post',
                url: ROOT_URL+'form/write_property/',
                data: {variable_property_id:variable_property_id, value:value},
                success: function (data) {

                },
                error: function(data) {
                    add_notification('write plug selected failed',3);
                }
            });
        }
    });

    //load top10 ranking at start
    reload_top10_ranking();

    $(window).on('hashchange', function() {
        //reset the pages settings to force the user to interact with
        reset_page(window.location.hash.substr(1));

        // Check if we are on a page that need to show the TOP10QAs
        refresh_top10_qa();
    });
});