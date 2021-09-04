<?php

function chat($uid){
  //dump($_GET);
  //var_dump($_POST);
  if (isset($_GET['Correspondence'])){
    $partner = $_GET['Correspondence'];
    $ord = 0;
  }

  if (isset($_GET['SendMes'])){
    return SendMes($_POST['MesText'], $partner, $uid, $ord);
  }
  elseif (isset($_GET['MessList'])){
    return MessList($partner, $ord, $uid, isset($_GET['all']));
  }
  elseif(isset($_GET['removeChatSeance'])){
    return RemoveChatSance($uid, $partner, $ord);
  }
  elseif(isset($_GET['TabInfoHtml'])){  
  }
  elseif(isset($_GET['SetActiveTab'])){
    $_SESSION['ChatActiveTab'] = $_GET['SetActiveTab'];
  }
  elseif(isset($_GET['getHeader'])){
    return getCorrespondenceHeader($partner);
  }
}

$websocket_ip = '127.0.0.1';
global $XmlRpc;
$XmlRpc = new XmlRpcClient($websocket_ip.':8765');

function getChatDomain(){
  return $GLOBALS['domain'];
}

function ActivateChatTab($user, $partner, $ord){
  wquery("insert ignore into chat_active_seances (user, partner, ord) values (%s,%s,%s)", array($user, $partner, $ord), false);
}

function RemoveChatSance($user, $partner, $ord){
  wquery("delete from chat_active_seances where user=%s and partner=%s and ord=%s", array($user, $partner, $ord));
}

function ShowChat($IdUser, $ChatParams){
  if (empty($IdUser))
    return "аккаунт не активен";
  if (!empty($_GET['active'])){
    list($partner, $ord) = explode('--', $_GET['active']);
    ActivateChatTab($IdUser, $partner, $ord);
  }
  //$ActiveOrds = getActiveOrders($IdUser);
  $pl = ChatPartnersList($IdUser);
  //dump($pl);
  
  $ChatParams['pl'] = json_encode($pl, JSON_HEX_TAG);
  if (empty($ChatParams['ActiveCorrespondence']) && isset($_SESSION['ChatActiveTab']))
    $ChatParams['ActiveCorrespondence'] = $_SESSION['ChatActiveTab'];
    
  return SmartyProcess(__DIR__.'/chat.html', $ChatParams);
}

global $UsersTable;
$UsersTable = array('tab'=>'users', 'f_id'=>'u_id', 'f_name'=>'u_name');

function ChatPartnersList($IdUser){  
  // вытаскиваем партнеров по переписке и смотрим сколько с каждым из них непрочитанных сообщений в обе стороны  
  global $UsersTable;
  $ret = wquery(" select cas.user,cas.partner, u.$UsersTable[f_name] TabHtml
      from chat_active_seances cas
	left join $UsersTable[tab] u on u.$UsersTable[f_id]=cas.partner
	where cas.user='%s'
	group by cas.user,cas.partner,cas.ord ", array($IdUser), false, 'partner');

  if (true){
    $sql = "select cas.partner,
      count(m1.t) OutTotal, count(m1.t_read) OutRead, max(m1.t) OutLastT, group_concat(if(m1.m_type=1,m1.text,null)) OutBlocked
      from chat_active_seances cas
      join chat_messages m1 on cas.partner=m1.to_u and m1.from_u='%s'
      where cas.user='%s'
      group by cas.partner";
    foreach ( wquery($sql, array($IdUser, $IdUser) ) as $v){
      $ret[$v['partner']] += $v;
      //$ret[$v['to_u']]['OutTotal'] = (int)$v['OutTotal'];
      //$ret[$v['to_u']]['OutUnread'] = $v['OutTotal'] - $v['OutRead'];      
    }
    $sql = "select cas.partner,
      count(m2.t) InTotal, count(m2.t+m2.t_read) InRead, max(m2.t) InLastT, group_concat(if(m2.m_type=1,m2.text,null)) InBlocked
      from chat_active_seances cas
      join chat_messages m2 on cas.partner=m2.from_u and m2.to_u='%s'
      where cas.user='%s'
      group by cas.partner";
    foreach ( wquery($sql, array($IdUser, $IdUser) ) as $v){
      $ret[$v['partner']] += $v;
    }
  }
  //dump($ret);

  return $ret;
}

function getCorrespondenceHeader($partner){
  global $UsersTable;  
  if ($u = wquery("select $UsersTable[f_name] from $UsersTable[tab] where $UsersTable[f_id]=%s ", array($partner))){
    return $u[0][$UsersTable['f_name']];
  }
  throw new exception ("не корректный собеседник: $partner");
}

function CreateChatSeance($user, $ToUser){
  //dump($ToUser);
  getCorrespondenceHeader($ToUser);
  
  if (empty($ToUser))
    throw new exception ('не понятно с кем хотим общаться');
  if ($user==$ToUser)
    throw new exception ('сами с собой не общаемся');
  wquery("insert ignore into chat_active_seances (user,partner) values ('%s','%s') ", array($user, $ToUser));
}


function SendMes($text, $ToUser, $FromUser, $ord=null, $mtype=0){
  sleep(0.7);
  $text = trim($text);
  if (strlen($text)==0)
    return 'пустое сообщение!';
  if (empty($ord))
    $ord = 0;
  wquery("insert into chat_messages (text,from_u,to_u,ord,m_type) values ('%s',%s,%s,%s,%s)", array($text, $FromUser, $ToUser, $ord, $mtype));
  if (!$mtype){ // для несестемных сообщений включаем сеансы обоим пользователям    
    ActivateChatTab($FromUser, $ToUser, $ord);
    ActivateChatTab($ToUser, $FromUser, $ord);
  }
  
  /*
   * нужно условие: если человека нет онлайн и последнее уведомление отправлялось не менее 3х часов
   * ещё: сравнивать время последнего уведомления и время последнего посещения......
  */
  //EmailSend::NewMes($ToUser, 4, 2, $FromUser);
  //EmailSend::SendProcess(array($ToUser));
  
  global $XmlRpc;
  $XmlRpc->call('SendChatState', array(getChatDomain(), $ToUser, json_encode(array('sound'=>true))));
  $ml = wquery("select *, unix_timestamp(t) t from chat_messages 
	  where ord=%s and from_u=%s and to_u=%s order by t desc limit 1", array($ord, $FromUser, $ToUser));
  return MessListProcess($ml, $FromUser, $ToUser);
}

function MessList($partner, $ord, $uid, $all){
  $sql = "select *, unix_timestamp(t) t from chat_messages where ord=%s and from_u in (%s,%s) and to_u in (%s,%s) ";
  if (!$all)
    $sql .= " and to_u!=%s and t_read is null ";
  $sql .= " order by -t  limit 150 ";
  $mess = wquery($sql, array($ord, $uid, $partner, $uid, $partner, $partner), false);
  return json_encode(MessListProcess(array_reverse($mess), $uid, $partner));
}

function MessListProcess($ml, $FromUser, $ToUser){
  sleep(0.2);
  foreach ($ml as &$mes){
    $mes['stat'] = 'mes'.($mes['from_u']==$FromUser ? 'Out' : 'In');
    
    $mes['text'] = nl2br(htmlspecialchars($mes['text']));
    
    //$preg = '/(https?:\/\/[\S]+)/';
    $preg = '/(https?:\/\/[\w\.\-\/\?\=]+)/';
    $mes['text'] = preg_replace($preg, '<a href="${1}" target="_blank"> ${1} </a> ', $mes['text']);  // замена ссылок
    
    if (empty($mes['t_read']) && $mes['stat']=='mesIn'){
      wquery("update chat_messages set t_read=current_timestamp where from_u=%s and to_u=%s and t=FROM_UNIXTIME(%s) ", 
	  array($mes['from_u'], $mes['to_u'], $mes['t']) );
    }
    $mes['t'] = strftime('%e %b %H:%M', $mes['t'] );
  }
  global $XmlRpc; 
  $XmlRpc->call('SendChatState', array(getChatDomain(), $FromUser, json_encode(array('MessStats'=> ChatPartnersList($FromUser)))));
  $XmlRpc->call('SendChatState', array(getChatDomain(), $ToUser,   json_encode(array('MessStats'=> ChatPartnersList($ToUser)))));  
  return $ml;
}

function OnWebsockConnect($uid){
  global $XmlRpc; 
  $XmlRpc->call('SendChatState', array(getChatDomain(), $uid, json_encode(array('MessStats'=> ChatPartnersList($uid)))));          
  // прверка активности и активизация юзера в БД
}

function OnWebsockDisconnect($uid){
  // деактивизация юзера в БД
}
