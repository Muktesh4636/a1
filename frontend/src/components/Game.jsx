import React, { useState, useEffect } from 'react';
import api from '../services/api';
import WalletWithdraw from './WalletWithdraw';
import WalletDeposit from './WalletDeposit';

export default function Game({ user, wallet, onRefreshWallet }) {
  const [currentRound, setCurrentRound] = useState(null);
  const [lastRound, setLastRound] = useState(null);
  const [timer, setTimer] = useState(0);
  const [myBets, setMyBets] = useState([]);
  const [selectedNumber, setSelectedNumber] = useState(null);
  const [betAmount, setBetAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [gameSettings, setGameSettings] = useState(null);
  const [showWithdraw, setShowWithdraw] = useState(false);
  const [showDeposit, setShowDeposit] = useState(false);

  useEffect(() => {
    loadGameData();
    loadGameSettings();
    
    // Auto-refresh every 5 seconds to keep round status updated
    const interval = setInterval(loadGameData, 5000);
    
    // Local timer countdown
    const timerInterval = setInterval(() => {
      setTimer(prev => {
        if (prev <= 0) return 0;
        const nextValue = prev + 1;
        // Use round_end_seconds from the current round if available
        const maxTime = currentRound?.round_end_seconds || 80;
        return nextValue > maxTime ? 1 : nextValue;
      });
    }, 1000);

    return () => {
      clearInterval(interval);
      clearInterval(timerInterval);
    };
  }, []);

  const loadGameData = async () => {
    try {
      const [roundData, betsData, lastRoundData] = await Promise.all([
        api.getCurrentRound(),
        api.getMyBets(),
        api.handleResponse(await fetch('/api/game/last-round-results/', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        })).catch(() => null)
      ]);
      setCurrentRound(roundData);
      setTimer(roundData.timer || 0);
      setMyBets(betsData);
      setLastRound(lastRoundData);
    } catch (err) {
      console.error('Failed to load game data:', err);
    }
  };

  const loadGameSettings = async () => {
    try {
      const settings = await api.getGameSettings();
      setGameSettings(settings);
    } catch (err) {
      console.error('Failed to load game settings:', err);
    }
  };

  const handleBet = async () => {
    if (!selectedNumber || !betAmount) {
      setMessage('Please select a number and enter bet amount');
      return;
    }

    const amount = parseFloat(betAmount);
    if (amount <= 0) {
      setMessage('Bet amount must be greater than 0');
      return;
    }

    if (amount > wallet?.balance) {
      setMessage('Insufficient balance');
      return;
    }

    try {
      setLoading(true);
      setMessage('');
      await api.placeBet(selectedNumber, amount);
      setMessage(`Bet placed successfully on number ${selectedNumber}!`);
      setBetAmount('');
      setSelectedNumber(null);
      loadGameData();
      onRefreshWallet?.();
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveBet = async (number) => {
    try {
      setLoading(true);
      await api.removeBet(number);
      setMessage(`Bet removed from number ${number}`);
      loadGameData();
      onRefreshWallet?.();
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getBetAmount = (number) => {
    const bet = myBets.find(b => b.number === number);
    return bet ? parseFloat(bet.chip_amount) : 0;
  };

  const getRoundStatus = () => {
    if (!currentRound) return 'Loading...';
    switch (currentRound.status) {
      case 'WAITING': return 'Waiting';
      case 'BETTING': return 'Open';
      case 'CLOSED': return 'Closed';
      case 'RESULT': return 'Result';
      case 'COMPLETED': return 'Done';
      default: return currentRound.status;
    }
  };

  const canBet = currentRound && currentRound.status === 'BETTING';

  // Dice Dot Component for realistic look
  const DiceDots = ({ number, isSelected }) => {
    const dotColor = isSelected ? 'bg-black' : 'bg-white';
    const diceBg = isSelected ? 'bg-amber-400' : 'bg-red-600';

    return (
      <div className={`dice-face relative w-12 h-12 ${diceBg} rounded-xl shadow-lg m-auto grid grid-cols-3 grid-rows-3 p-2 transition-colors duration-300`}>
        {number === 1 && <div className={`col-start-2 row-start-2 ${dotColor} rounded-full m-auto w-2.5 h-2.5 shadow-sm`}></div>}
        {number === 2 && (
          <>
            <div className={`col-start-1 row-start-1 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-3 row-start-3 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
          </>
        )}
        {number === 3 && (
          <>
            <div className={`col-start-1 row-start-1 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-2 row-start-2 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-3 row-start-3 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
          </>
        )}
        {number === 4 && (
          <>
            <div className={`col-start-1 row-start-1 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-3 row-start-1 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-1 row-start-3 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-3 row-start-3 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
          </>
        )}
        {number === 5 && (
          <>
            <div className={`col-start-1 row-start-1 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-3 row-start-1 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-2 row-start-2 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-1 row-start-3 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-3 row-start-3 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
          </>
        )}
        {number === 6 && (
          <>
            <div className={`col-start-1 row-start-1 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-3 row-start-1 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-1 row-start-2 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-3 row-start-2 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-1 row-start-3 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
            <div className={`col-start-3 row-start-3 ${dotColor} rounded-full m-auto w-2 h-2 shadow-sm`}></div>
          </>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Top Bar: Round & Balance */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-4 flex flex-col justify-center border-l-4 border-l-blue-500">
          <div className="flex justify-between items-start">
            <h2 className="text-white/60 text-xs uppercase tracking-wider font-bold mb-1">Current Round</h2>
            <div className="text-right">
              <span className="text-[10px] font-black text-white/40 uppercase tracking-widest">Time</span>
              <p className="text-xl font-black text-amber-400 leading-none">{timer}s</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-2xl font-black text-white">#{currentRound?.round_id?.slice(-4) || '---'}</span>
            <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase ${
              canBet ? 'bg-green-500 text-black animate-pulse' : 'bg-red-500/20 text-red-400'
            }`}>
              {getRoundStatus()}
            </span>
          </div>
        </div>

        <div className="glass-panel-gold p-4 flex justify-between items-center relative overflow-hidden group border-l-4 border-l-amber-500">
          <div className="absolute right-0 top-0 opacity-10 group-hover:scale-110 transition-transform pointer-events-none">
            <span className="text-6xl">💰</span>
          </div>
          <div className="relative z-10">
            <h2 className="text-amber-200/60 text-xs uppercase tracking-wider font-bold mb-1">Your Balance</h2>
            <p className="text-3xl font-black text-amber-400">₹{wallet?.balance || '0.00'}</p>
          </div>
          <div className="flex gap-3 relative z-10">
            <button
              onClick={() => { setShowDeposit(!showDeposit); setShowWithdraw(false); }}
              className={`px-4 py-2 flex items-center gap-2 rounded-xl shadow-lg transition-all active:scale-95 font-bold text-xs ${
                showDeposit ? 'bg-white text-blue-600' : 'bg-blue-600 hover:bg-blue-500 text-white'
              }`}
            >
              <span>{showDeposit ? '✕' : '➕'}</span>
              <span>DEPOSIT</span>
            </button>
            <button
              onClick={() => { setShowWithdraw(!showWithdraw); setShowDeposit(false); }}
              className={`px-4 py-2 flex items-center gap-2 rounded-xl shadow-lg transition-all active:scale-95 font-bold text-xs ${
                showWithdraw ? 'bg-white text-orange-600' : 'bg-orange-600 hover:bg-orange-500 text-white'
              }`}
            >
              <span>{showWithdraw ? '✕' : '💸'}</span>
              <span>WITHDRAW</span>
            </button>
          </div>
        </div>

        <div className="glass-panel p-4 flex items-center justify-between border-l-4 border-l-indigo-500">
          <div className="flex -space-x-2">
             {[1,2,3,4].map(i => (
               <div key={i} className="w-9 h-9 rounded-full border-2 border-slate-800 bg-gradient-to-br from-indigo-400 to-purple-600 flex items-center justify-center text-[10px] text-white font-bold shadow-lg">
                 {String.fromCharCode(64 + i)}
               </div>
             ))}
             <div className="w-9 h-9 rounded-full border-2 border-slate-800 bg-slate-700 flex items-center justify-center text-[10px] text-white/60 shadow-lg">
               +12
             </div>
          </div>
          <div className="text-right">
            <p className="text-white/40 text-[10px] font-bold uppercase tracking-widest">Live Players</p>
            <p className="text-white font-black text-lg">16 ACTIVE</p>
          </div>
        </div>
      </div>

      {/* Quick Actions (Deposit/Withdraw) */}
      <div className="space-y-4">
        {showDeposit && (
          <div className="glass-panel border-blue-500/50 p-6 animate-fadeIn relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-3">
                <span className="w-10 h-10 flex items-center justify-center bg-blue-500 rounded-xl text-lg shadow-lg">💰</span> 
                Deposit Funds
              </h3>
              <button onClick={() => setShowDeposit(false)} className="w-8 h-8 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 text-white transition-colors">&times;</button>
            </div>
            <WalletDeposit 
              user={user}
              onSuccess={() => { onRefreshWallet?.(); setShowDeposit(false); }} 
            />
          </div>
        )}

        {showWithdraw && (
          <div className="glass-panel border-orange-500/50 p-6 animate-fadeIn relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-orange-500"></div>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-3">
                <span className="w-10 h-10 flex items-center justify-center bg-orange-500 rounded-xl text-lg shadow-lg">💸</span> 
                Withdrawal
              </h3>
              <button onClick={() => setShowWithdraw(false)} className="w-8 h-8 flex items-center justify-center rounded-full bg-white/5 hover:bg-white/10 text-white transition-colors">&times;</button>
            </div>
            <WalletWithdraw onSuccess={() => { onRefreshWallet?.(); setShowWithdraw(false); }} />
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Betting Area */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-6 relative overflow-hidden min-h-[500px] flex flex-col">
             {/* Decorative background grid */}
             <div className="absolute inset-0 opacity-5 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)', backgroundSize: '32px 32px' }}></div>
             
             <div className="flex justify-between items-center mb-10 relative z-10">
               <div>
                 <h3 className="text-2xl font-black text-white tracking-tighter italic">LUCKY ROLL</h3>
                 <p className="text-white/40 text-xs font-bold uppercase tracking-[0.2em]">Select your number to win</p>
               </div>
               
               {/* 6 Dice Display (Current or Last Round) */}
               {(currentRound?.dice_1 || lastRound?.dice_1) && (
                 <div className="flex flex-col items-center gap-2">
                   <span className="text-[9px] font-black text-white/20 uppercase tracking-widest leading-none">
                     {currentRound?.dice_1 ? 'Current Result' : `Last Round (#${lastRound?.round_id?.slice(-4)})`}
                   </span>
                   <div className="flex gap-2 bg-black/40 p-3 rounded-2xl border border-white/5 shadow-inner">
                     {[1, 2, 3, 4, 5, 6].map(i => {
                       const diceVal = currentRound?.dice_1 ? currentRound[`dice_${i}`] : lastRound[`dice_${i}`];
                       return (
                         <div key={i} className="scale-75 origin-center">
                           <DiceDots number={diceVal} isSelected={false} />
                         </div>
                       );
                     })}
                   </div>
                 </div>
               )}

               {canBet && (
                 <div className="px-4 py-2 bg-yellow-500/10 border border-yellow-500/20 rounded-xl flex items-center gap-3">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full animate-ping"></div>
                    <span className="text-yellow-500 text-xs font-black tracking-widest uppercase">Betting Live</span>
                 </div>
               )}
             </div>

             {message && (
               <div className="mb-8 p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl text-indigo-100 text-sm animate-fadeIn flex items-center gap-4 relative z-10">
                 <div className="w-10 h-10 flex-shrink-0 bg-indigo-500/20 rounded-full flex items-center justify-center text-xl">💡</div>
                 <span className="font-medium">{message}</span>
               </div>
             )}

             <div className="grid grid-cols-2 sm:grid-cols-3 gap-6 mb-10 relative z-10 flex-grow">
               {[1, 2, 3, 4, 5, 6].map((number) => {
                 const currentBet = getBetAmount(number);
                 const isSelected = selectedNumber === number;
                 
                 return (
                   <button
                     key={number}
                     onClick={() => canBet && setSelectedNumber(number)}
                     disabled={!canBet}
                     className={`group relative p-8 rounded-3xl border-2 transition-all duration-500 overflow-hidden ${
                       isSelected 
                         ? 'bg-amber-400 border-amber-300 scale-[1.05] shadow-[0_20px_40px_rgba(245,158,11,0.25)]' 
                         : currentBet > 0
                         ? 'bg-green-600/20 border-green-500/50'
                         : 'bg-white/5 border-white/10 hover:border-white/30 hover:bg-white/10'
                     } ${!canBet ? 'opacity-50 cursor-not-allowed' : 'active:scale-95'}`}
                   >
                     {/* Gloss effect for selected */}
                     {isSelected && (
                       <div className="absolute top-0 left-0 w-full h-1/2 bg-gradient-to-b from-white/30 to-transparent pointer-events-none"></div>
                     )}
                     
                     <div className="flex flex-col items-center gap-6 relative z-10">
                        <DiceDots number={number} isSelected={isSelected} />
                        <div className="text-center">
                          <span className={`block text-[10px] font-black uppercase tracking-[0.3em] mb-1 ${isSelected ? 'text-black/40' : 'text-white/30'}`}>Select</span>
                          <span className={`text-4xl font-black leading-none ${isSelected ? 'text-black' : 'text-white'}`}>{number}</span>
                        </div>
                     </div>

                     {currentBet > 0 && (
                       <div className="absolute -top-1 -right-1 px-4 py-2 bg-green-500 text-black text-xs font-black rounded-bl-2xl shadow-xl border-l-2 border-b-2 border-slate-900/50">
                         ₹{currentBet.toFixed(0)}
                       </div>
                     )}
                   </button>
                 );
               })}
             </div>

             {canBet && (
               <div className="bg-white/5 rounded-3xl p-8 border border-white/10 animate-fadeIn relative z-10">
                 <div className="flex flex-col md:flex-row gap-8 items-end">
                    <div className="flex-1 w-full">
                      <div className="flex justify-between items-center mb-3">
                        <label className="text-white/60 text-[10px] font-black uppercase tracking-[0.2em]">Amount to Wager</label>
                        <div className="flex gap-2">
                           {[10, 50, 100, 500].map(amt => (
                             <button 
                              key={amt}
                              onClick={() => setBetAmount(amt.toString())}
                              className="px-3 py-1 bg-white/5 hover:bg-white/10 rounded-lg text-[10px] text-white/80 font-black border border-white/10 transition-colors"
                             >
                               +{amt}
                             </button>
                           ))}
                        </div>
                      </div>
                      <div className="relative group">
                        <span className="absolute left-6 top-1/2 -translate-y-1/2 text-amber-500 font-black text-2xl group-focus-within:scale-110 transition-transform">₹</span>
                        <input
                          type="number"
                          value={betAmount}
                          onChange={(e) => setBetAmount(e.target.value)}
                          className="w-full pl-12 pr-6 py-5 rounded-2xl bg-black/60 text-white font-black text-3xl border-2 border-white/5 focus:border-amber-500 focus:bg-black/80 focus:outline-none transition-all placeholder:text-white/10 shadow-inner"
                          placeholder="0.00"
                        />
                      </div>
                    </div>
                    <div className="flex gap-4 w-full md:w-auto">
                      <button
                        onClick={handleBet}
                        disabled={loading || !selectedNumber || !betAmount}
                        className="flex-1 md:flex-none px-12 py-5 bg-gradient-to-r from-amber-400 via-amber-500 to-orange-500 text-black font-black text-xl rounded-2xl hover:brightness-110 disabled:opacity-30 disabled:grayscale disabled:cursor-not-allowed transition-all shadow-[0_15px_30px_rgba(245,158,11,0.3)] active:translate-y-1 active:shadow-none uppercase tracking-tighter"
                      >
                        {loading ? 'WAITING...' : 'PLACE BET'}
                      </button>
                      {selectedNumber && getBetAmount(selectedNumber) > 0 && (
                        <button
                          onClick={() => handleRemoveBet(selectedNumber)}
                          disabled={loading}
                          className="w-16 flex items-center justify-center bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white rounded-2xl border-2 border-red-500/20 transition-all active:scale-95"
                          title="Clear Bet"
                        >
                          🗑️
                        </button>
                      )}
                    </div>
                 </div>
               </div>
             )}

             {!canBet && (
               <div className="flex-grow flex flex-col items-center justify-center py-20 bg-white/5 rounded-3xl border-2 border-dashed border-white/5 relative z-10">
                 <div className="relative mb-8">
                    <div className="text-7xl animate-bounce">🎲</div>
                    <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-12 h-2 bg-black/40 rounded-full blur-md"></div>
                 </div>
                 <h3 className="text-2xl font-black text-white mb-2 uppercase tracking-tighter italic">Round Processing</h3>
                 <p className="text-white/40 text-sm font-medium max-w-xs text-center leading-relaxed">
                   The dice are in the air! Betting is currently locked. New round starting in moments.
                 </p>
                 <button 
                  onClick={loadGameData} 
                  className="mt-10 px-8 py-3 bg-white/10 hover:bg-white/20 text-white rounded-2xl text-xs font-black tracking-widest uppercase transition-all flex items-center gap-2"
                 >
                   <span className="animate-spin text-lg">↻</span> Sync Game
                 </button>
               </div>
             )}
          </div>
        </div>

        {/* Sidebar Info */}
        <div className="space-y-6">
          {/* Payout Guide */}
          <div className="glass-panel p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/10 rounded-full -mr-12 -mt-12 blur-3xl"></div>
            <h3 className="text-white font-black text-xs uppercase tracking-[0.3em] mb-8 flex items-center gap-3">
              <span className="w-6 h-6 bg-amber-500 rounded flex items-center justify-center text-[10px] text-black italic">!</span>
              Multiplier Table
            </h3>
            <div className="space-y-4">
              {[
                { count: 1, multi: '2.0x', desc: 'MATCH 1' },
                { count: 2, multi: '4.0x', desc: 'MATCH 2' },
                { count: 3, multi: '6.0x', desc: 'MATCH 3' },
                { count: 4, multi: '8.0x', desc: 'MATCH 4' },
                { count: 5, multi: '10.0x', desc: 'JACKPOT' },
              ].map((row) => (
                <div key={row.count} className="payout-card p-4 flex justify-between items-center group hover:bg-white/5 transition-all rounded-2xl cursor-default">
                  <div>
                    <p className="text-white font-black text-base italic leading-none">{row.desc}</p>
                    <p className="text-white/30 text-[9px] font-bold uppercase tracking-widest mt-1">{row.count} Dice Match</p>
                  </div>
                  <div className="text-amber-400 font-black text-2xl tracking-tighter group-hover:scale-110 transition-transform origin-right">
                    {row.multi}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Active Bets Sidebar */}
          <div className="glass-panel p-6">
            <h3 className="text-white font-black text-xs uppercase tracking-[0.3em] mb-8 flex items-center gap-3">
              <span className="w-6 h-6 bg-indigo-500 rounded flex items-center justify-center text-[10px] text-white">★</span>
              Active Stakes
            </h3>
            {myBets.length === 0 ? (
              <div className="text-center py-12 bg-black/20 rounded-2xl border border-white/5">
                <p className="text-white/20 text-[10px] font-black uppercase tracking-widest">No bets placed</p>
              </div>
            ) : (
              <div className="space-y-4">
                {myBets.map((bet) => (
                  <div key={bet.number} className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5 hover:border-white/10 transition-colors">
                    <div className="flex items-center gap-4">
                       <div className="w-10 h-10 bg-red-600 rounded-xl flex items-center justify-center font-black text-white shadow-lg text-lg">
                         {bet.number}
                       </div>
                       <div>
                         <p className="text-white text-xs font-black italic uppercase">Dice {bet.number}</p>
                         <p className="text-white/30 text-[9px] font-bold uppercase">{new Date(bet.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
                       </div>
                    </div>
                    <div className="text-right">
                      <p className="text-green-400 font-black text-lg tracking-tighter">₹{parseFloat(bet.chip_amount).toFixed(0)}</p>
                    </div>
                  </div>
                ))}
                <div className="pt-4 border-t border-white/10 flex justify-between items-center">
                  <span className="text-white/40 text-[10px] font-black uppercase tracking-widest">Total Stake</span>
                  <span className="text-white font-black">₹{myBets.reduce((acc, b) => acc + parseFloat(b.chip_amount), 0).toFixed(0)}</span>
                </div>
              </div>
            )}
          </div>
          
          {/* Support/Promo Card */}
          <div className="bg-gradient-to-br from-indigo-700 via-purple-700 to-pink-700 rounded-3xl p-8 text-white shadow-2xl relative overflow-hidden group cursor-pointer">
             <div className="absolute -right-6 -bottom-6 text-9xl opacity-20 rotate-12 group-hover:rotate-0 transition-transform duration-700">🎰</div>
             <div className="relative z-10">
               <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center mb-6 backdrop-blur-md">
                 <span className="text-xl">🛡️</span>
               </div>
               <h4 className="text-2xl font-black mb-3 italic tracking-tighter">Safe Play</h4>
               <p className="text-sm text-white/70 font-medium leading-relaxed mb-6">
                 All outcomes are verified and payouts are instant. Play responsibly and set your own limits.
               </p>
               <button className="w-full py-3 bg-white text-indigo-700 font-black rounded-xl text-xs uppercase tracking-widest hover:bg-indigo-50 transition-colors">
                 Help Center
               </button>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
